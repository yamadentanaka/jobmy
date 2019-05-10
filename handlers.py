import tornado.web
import logging
import traceback
import json

import jobmy_tables
import job
from lib.string_utils import is_empty, is_int
import settings

class BaseJsonApiHandler(tornado.web.RequestHandler):
    def post(self):
        logging.debug("base json api handler start.")
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        out = self.make_json_dict()
        self.write(json.dumps(out))
        logging.debug("base json api handler end.")

    def make_json_dict(self):
        return {}

class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("OK")

class TopHandler(tornado.web.RequestHandler):
    def get(self):
        logging.debug("top handler start.")
        jobs = jobmy_tables.get_job_history_latest(10)
        self.render("index.html", jobs=jobs)
        logging.debug("top handler end.")

class JobListHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info("job list handler start.")
        jobs = jobmy_tables.get_all_jobs()
        self.render("job_list.html", jobs=jobs)
        logging.info("job list handler end.")

class JobHistoryDetailHandler(tornado.web.RequestHandler):
    def get(self):
        logging.info("job history detail handler start.")
        job_id = self.get_argument("job_id", None)
        if job_id is None:
            self.redirect("/")
        job = jobmy_tables.get_job_history_by_job_id(job_id)
        self.render("job_history_detail.html", job=job)
        logging.info("job history detail handler end.")

class JobEditHandler(BaseJsonApiHandler):
    def get(self):
        logging.debug("job edit handler start.")
        job_id = self.get_argument("job_id", None)
        if job_id:
            job = jobmy_tables.get_job_by_id(job_id)
            self.render("job_edit.html",
                title=job["TITLE"],
                remarks=job["REMARKS"],
                command=job["COMMAND"],
                schedule=job["SCHEDULE"],
                max_exec_time=job["MAX_EXEC_TIME"],
                next_job_ids=job["NEXT_JOB_IDS"],
                job_id=job["ID"]
            )
        else:
            self.render("job_edit.html",
                title=None,
                remarks=None,
                command=None,
                schedule=None,
                max_exec_time=None,
                next_job_ids=None,
                job_id=None
            )
        logging.debug("job edit handler end.")

    def make_json_dict(self):
        logging.debug("job edit handler start.")
        job_id = self.get_argument("job_id", None)
        title = self.get_argument("title", None)
        remarks = self.get_argument("remarks", None)
        command = self.get_argument("command", None)
        schedule = self.get_argument("schedule", None)
        max_exec_time = self.get_argument("max_exec_time", None)
        next_job_ids = self.get_argument("next_job_ids", None)
        msg = "ok"
        out = {
            "msg": msg,
            "title": title,
            "remarks": remarks,
            "command": command,
            "schedule": schedule,
            "max_exec_time": max_exec_time,
            "next_job_ids": next_job_ids
        }
        if not is_empty(title) and not is_empty(remarks) and \
            not is_empty(command) and not is_empty(schedule) and \
            not is_empty(max_exec_time):
            if job_id:
                logging.debug("update job. ID: {}".format(job_id))
                ret = jobmy_tables.update_job(job_id, title, remarks, command, schedule, max_exec_time, next_job_ids, settings.HOST_NAME)
            else:
                logging.debug("insert job.")
                ret = jobmy_tables.insert_job(title, remarks, command, schedule, max_exec_time, next_job_ids, settings.HOST_NAME)
            if ret:
                out["result"] = 0
            else:
                out["result"] = 1
                out["msg"] = "failed."
        else:
            out["result"] = 1
            out["msg"] = "Please input all params except for the next job ids."
        logging.debug("job edit handler end.")
        return out

class ExecuteJobHandler(BaseJsonApiHandler):
    def make_json_dict(self):
        logging.debug("execute job handler start.")
        job_id = self.get_argument("job_id", None)
        if is_int(job_id):
            job.kick_job(int(job_id))
            out = {"result": 0, "msg": "ok"}
        else:
            logging.warning("job_id is invalid. {}".format(job_id))
            out = {"result": 1, "msg": "failed to job execute."}
        logging.debug("execute job handler end.")
        return out

class KillJobHandler(BaseJsonApiHandler):
    def make_json_dict(self):
        logging.debug("kill job handler start.")
        job_key = self.get_argument("job_key", None)
        job.kill_job(job_key)
        out = {"result": 0, "msg": "ok"}
        logging.debug("execute kill handler end.")
        return out
