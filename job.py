import os
import socket
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor

import jobmy_tables
import settings
import uuid

def kick_job(job_id):
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(execute_job, job_id)

def execute_job(job_id):
    try:
        # get job info
        job = jobmy_tables.get_job_by_id(job_id)
        # create work directory
        key = str(uuid.uuid4())
        tmp_dir = os.path.join(settings.WORK_DIR, key)
        os.makedirs(tmp_dir)
        # create exec shell script
        shell_file = os.path.join(tmp_dir, "jobmy.sh")
        with open(shell_file, "w") as wfp:
            wfp.write("#!/bin/bash\n\n")
            wfp.write("cd `dirname $0`\n\n")
            wfp.write(job["COMMAND"])
        p = Path(shell_file)
        p.chmod(0o764)
        # insert history table
        value_dict = {}
        value_dict["JOB_ID"] = job_id
        value_dict["JOB_KEY"] = key
        value_dict["HOST"] = socket.gethostname()
        value_dict["EXEC_RESULT"] = "processing"
        value_dict["START_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # execute job
        cmd = "{}".format(os.path.abspath(shell_file))
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        value_dict["PID"] = result.pid
        ret = jobmy_tables.insert_job_history(value_dict)
        if not ret:
            logging.warning("JOB KEY {} is failed to insert record.".format(key))
        result.wait()
        # update history table
        value_dict["EXEC_RESULT"] = "successed" if result.returncode == 0 else "failed"
        out, err = result.communicate()
        value_dict["STD_OUT"] = out
        value_dict["STD_ERR"] = err
        value_dict["END_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ret = jobmy_tables.update_job_history(value_dict)
        if not ret:
            logging.warning("JOB KEY {} is failed to update record.".format(key))
    except Exception as ex:
        logging.error(traceback.format_exc())
