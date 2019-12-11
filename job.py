import os
import platform
import traceback
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

import settings
if settings.DB_TYPE == "MySQL":
    import jobmy_tables
elif settings.DB_TYPE == "SQLite":
    import jobmy_tables_sqlite as jobmy_tables
from lib import cron_utils
from lib.network_utils import send_slack

JOBMY_JOB_INFO = {
    "JOBS": {},
    "PROCESSES": {}
}

class Job:
    def __init__(self, job_id, caller_job_key=None):
        self.job_id = job_id
        self.caller_job_key = caller_job_key
        self.key = str(uuid.uuid4())
        self.value_dict = {}
        self.result = None

    def execute_job(self):
        logging.info("start job: {}, key: {}".format(self.job_id, self.key))
        try:
            # get job info
            job = jobmy_tables.get_job_by_id(self.job_id)
            # create work directory
            tmp_dir = os.path.join(settings.WORK_DIR, self.key)
            os.makedirs(tmp_dir)
            # create exec shell script
            if platform.system() == "Windows":
                shell_file = os.path.join(tmp_dir, "jobmy.bat")
                with open(shell_file, "w") as wfp:
                    wfp.write("@echo off\n\n")
                    wfp.write("cd %~dp0\n\n")
                    wfp.write(job["COMMAND"])
            else:
                shell_file = os.path.join(tmp_dir, "jobmy.sh")
                with open(shell_file, "w") as wfp:
                    wfp.write("#!/bin/bash\n\n")
                    wfp.write("cd `dirname $0`\n\n")
                    wfp.write(job["COMMAND"])
            p = Path(shell_file)
            p.chmod(0o764)
            # insert history table
            self.value_dict["JOB_ID"] = self.job_id
            self.value_dict["JOB_KEY"] = self.key
            if self.caller_job_key:
                self.value_dict["CALLER_JOB_KEY"] = self.caller_job_key
            self.value_dict["HOST"] = settings.HOST_NAME
            host_name = socket.gethostname()
            try:
                ip = socket.gethostbyname(host_name)
            except:
                ip = ""
            self.value_dict["IP_ADDRESS"] = ip
            self.value_dict["EXEC_RESULT"] = "running"
            self.value_dict["START_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.value_dict["COMMAND"] = job["COMMAND"]
            # execute job
            cmd = "{}".format(os.path.abspath(shell_file))
            if platform.system() == "Windows":
                self.result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
            else:
                self.result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)
            self.value_dict["PID"] = self.result.pid
            ret = jobmy_tables.insert_job_history(self.value_dict)
            if not ret:
                logging.warning("JOB KEY {} is failed to insert record.".format(self.key))
            JOBMY_JOB_INFO["JOBS"][self.key] = self.value_dict
            JOBMY_JOB_INFO["PROCESSES"][self.key] = self.result
            send_slack("job[{}] key[{}] started.".format(job["TITLE"], self.key))
            self.result.wait()
            # update history table
            self.value_dict["RETURN_CODE"] = self.result.returncode
            if self.result.returncode == 0:
                self.value_dict["EXEC_RESULT"] = "successed"
            elif self.result.returncode == -9:
                self.value_dict["EXEC_RESULT"] = "killed"
            else:
                self.value_dict["EXEC_RESULT"] = "failed"
            out, err = self.result.communicate()
            self.value_dict["STD_OUT"] = out
            self.value_dict["STD_ERR"] = err
            self.value_dict["END_DATETIME"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # if it takes too long, job will maybe be killed.
            if self.key in JOBMY_JOB_INFO["PROCESSES"]:
                self.finish_job()
            send_slack("job[{}] key[{}] is end.".format(job["TITLE"], self.key))
            # when job successed, tmp directory remove
            if self.result.returncode == 0:
                logging.info("remove dir {}".format(tmp_dir))
                shutil.rmtree(tmp_dir)
                # when next_job_ids is exists, kick its jobs.
                if job["NEXT_JOB_IDS"] is not None:
                    ids = job["NEXT_JOB_IDS"].split(",")
                    for next_job_id in ids:
                        if next_job_id != "":
                            kick_job(int(next_job_id), caller_job_key=self.key)
        except Exception as ex:
            logging.error(traceback.format_exc())
        logging.info("end job: {}, key: {}".format(self.job_id, self.key))

    def finish_job(self):
        ret = jobmy_tables.update_job_history(self.value_dict)
        if not ret:
            logging.warning("JOB KEY {} is failed to update record.".format(self.key))
        if self.key in JOBMY_JOB_INFO["JOBS"]:
            JOBMY_JOB_INFO["JOBS"].pop(self.key)
        if self.key in JOBMY_JOB_INFO["PROCESSES"]:
            JOBMY_JOB_INFO["PROCESSES"].pop(self.key)

def kick_job(job_id, caller_job_key=None):
    job = Job(job_id, caller_job_key=caller_job_key)
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(job.execute_job)

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
            if platform.system() == "Windows":
                logging.info("windows kill process.")
                cmd = "taskkill /F /T /pid {}".format(process_id)
                result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
                result.wait()
                JOBMY_JOB_INFO["JOBS"][job_key]["KILLED"] = True
                # os.kill(process_id, signal.CTRL_C_EVENT)
            else:
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
