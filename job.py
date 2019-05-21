import os
import psutil
import signal
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
from lib import cron_utils

JOBMY_JOB_INFO = {
    "JOBS": {},
    "PROCESSES": {}
}

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
        value_dict["COMMAND"] = job["COMMAND"]
        # execute job
        cmd = "{}".format(os.path.abspath(shell_file))
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)
        value_dict["PID"] = result.pid
        ret = jobmy_tables.insert_job_history(value_dict)
        if not ret:
            logging.warning("JOB KEY {} is failed to insert record.".format(key))
        JOBMY_JOB_INFO["JOBS"][key] = value_dict
        JOBMY_JOB_INFO["PROCESSES"][key] = result
        result.wait()
        # update history table
        value_dict["RETURN_CODE"] = result.returncode
        if result.returncode == 0:
            value_dict["EXEC_RESULT"] = "successed"
        elif result.returncode == -9:
            value_dict["EXEC_RESULT"] = "killed"
        else:
            value_dict["EXEC_RESULT"] = "failed"
        out, err = result.communicate()
        value_dict["STD_OUT"] = out
        value_dict["STD_ERR"] = err
        value_dict["END_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if key in JOBMY_JOB_INFO["PROCESSES"]:
            finish_job(value_dict)
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

def finish_job(value_dict):
    ret = jobmy_tables.update_job_history(value_dict)
    if not ret:
        logging.warning("JOB KEY {} is failed to update record.".format(value_dict["JOB_KEY"]))
    if value_dict["JOB_KEY"] in JOBMY_JOB_INFO["JOBS"]:
        JOBMY_JOB_INFO["JOBS"].pop(value_dict["JOB_KEY"])
    if value_dict["JOB_KEY"] in JOBMY_JOB_INFO["PROCESSES"]:
        JOBMY_JOB_INFO["PROCESSES"].pop(value_dict["JOB_KEY"])

def kill_job(job_key):
    error_value_dict = {
        "RETURN_CODE": -9,
        "EXEC_RESULT": "killed",
        "STD_OUT": None,
        "STD_ERR": None,
        "END_DATETIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "JOB_KEY": job_key
    }
    if job_key in JOBMY_JOB_INFO["PROCESSES"]:
        # JOBMY_JOB_INFO["PROCESSES"][job_key].kill()
        process_id = JOBMY_JOB_INFO["JOBS"][job_key]["PID"]
        if psutil.pid_exists(process_id):
            os.killpg(process_id, signal.SIGKILL)
            logging.info("killed PID: {}, KEY: {}".format(JOBMY_JOB_INFO["JOBS"][job_key]["PID"], job_key))
        else:
            logging.warning("kill target job is not existed. {}".format(job_key))
            jobmy_tables.update_job_history(error_value_dict)
    else:
        logging.warning("kill target job is not existed. {}".format(job_key))
        jobmy_tables.update_job_history(error_value_dict)

def kill_jobs():
    targets = jobmy_tables.get_kill_target_jobs()
    if len(targets) > 0:
        logging.info("kill target jobs: {}".format(len(targets)))
        for target in targets:
            kill_job(target["JOB_KEY"])
            logging.info("{} {} was killed.".format(target["JOB_KEY"], target["TITLE"]))

def kick_schedule_jobs():
    jobs = jobmy_tables.get_all_jobs()
    for j in jobs:
        if j["SCHEDULE"].lower() != "immediate":
            if cron_utils.is_executable(j["SCHEDULE"]):
                # if running jobs exists, skip.
                running_jobs = jobmy_tables.get_running_jobs_by_id(j["ID"])
                if len(running_jobs) > 0:
                    # insert history table
                    key = str(uuid.uuid4())
                    value_dict = {}
                    value_dict["JOB_ID"] = j["ID"]
                    value_dict["JOB_KEY"] = key
                    value_dict["HOST"] = settings.HOST_NAME
                    host_name = socket.gethostname()
                    ip = socket.gethostbyname(host_name)
                    value_dict["IP_ADDRESS"] = ip
                    value_dict["PID"] = None
                    value_dict["EXEC_RESULT"] = "skipped"
                    value_dict["START_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ret = jobmy_tables.insert_job_history(value_dict)
                    if not ret:
                        logging.warning("JOB KEY {} is failed to insert record.".format(key))
                    logging.info("skip job: {} {}".format(j["ID"], j["TITLE"]))
                else:
                    logging.info("now kick job: {} {}".format(j["ID"], j["TITLE"]))
                    kick_job(j["ID"])
