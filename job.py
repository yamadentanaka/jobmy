import os
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

import jobmy_tables
import settings
import uuid

def execute_job(job_id):
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
    value_dict["EXEC_RESULT"] = "processing"
    value_dict["START_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ret = jobmy_tables.insert_job_history(value_dict)
    # execute job
    cmd = "{}".format(os.path.abspath(shell_file))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # update history table
    value_dict["EXEC_RESULT"] = "successed" if result.returncode == 0 else "failed"
    value_dict["STD_OUT"] = result.stdout
    value_dict["STD_ERR"] = result.stderr
    value_dict["END_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ret = jobmy_tables.update_job_history(value_dict)
