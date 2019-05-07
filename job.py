import os
import shutil
import socket
import uuid
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import jobmy_tables
import settings
from lib import string_utils, cron_utils

def schedule_analysis(value, last_exec_time):
    if value.lower() == "immediate":
        return True
    checker = cron_utils.ExecutableChecker(value, last_exec_time)
    result = checker.is_executable()
    return result

def kick_job(job_id, caller_job_key=None):
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(lambda x,y:execute_job(x, caller_job_key=y), job_id, caller_job_key)

def execute_job(job_id, caller_job_key=None):
    key = str(uuid.uuid4())
    logging.info("start job: {}, key: {}".format(job_id, key))
    try:
        # get job info
        job = jobmy_tables.get_job_by_id(job_id)
        # create work directory
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
        if caller_job_key:
            value_dict["CALLER_JOB_KEY"] = caller_job_key
        value_dict["HOST"] = settings.HOST_NAME
        host_name = socket.gethostname()
        ip = socket.gethostbyname(host_name)
        value_dict["IP_ADDRESS"] = ip
        value_dict["EXEC_RESULT"] = "running"
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
        # when job successed, tmp directory remove
        if result.returncode == 0:
            logging.info("remove dir {}".format(tmp_dir))
            shutil.rmtree(tmp_dir)
            # when next_job_ids is exists, kick its jobs.
            if job["NEXT_JOB_IDS"] is not None:
                ids = job["NEXT_JOB_IDS"].split(",")
                for next_job_id in ids:
                    kick_job(int(next_job_id), caller_job_key=key)
    except Exception as ex:
        logging.error(traceback.format_exc())
    logging.info("end job: {}, key: {}".format(job_id, key))

def kill_jobs():
    targets = jobmy_tables.get_kill_target_jobs()
    logging.info("kill target jobs: {}".format(len(targets)))
