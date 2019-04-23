import tornado.web
import logging
import traceback
import json

import jobmy_tables
from lib.string_utils import is_empty

class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("OK")

class TopHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        logging.debug("top handler start.")
        jobs = jobmy_tables.get_all_jobs()
        self.render("index.html", jobs=jobs)
        logging.debug("top handler end.")

class JobEditHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        logging.debug("job edit handler start.")
        job_id = self.get_argument("job_id", None)
        if job_id:
            job = jobmy_tables.get_job_by_id(job_id)
            self.render("job_edit.html",
                title=job["TITLE"],
                remarks=job["REMARKS"],
                command=job["COMMAND"],
                schedule=job["SCHEDULE"]
            )
        else:
            self.render("job_edit.html",
                title=None,
                remarks=None,
                command=None,
                schedule=None
            )
        logging.debug("job edit handler end.")

    def post(self):
        logging.debug("job edit handler start.")
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        job_id = self.get_argument("job_id", None)
        title = self.get_argument("title", None)
        remarks = self.get_argument("remarks", None)
        command = self.get_argument("command", None)
        schedule = self.get_argument("schedule", None)
        msg = "ok"
        out = {
            "msg": msg,
            "title": title,
            "remarks": remarks,
            "command": command,
            "schedule": schedule
        }
        if not is_empty(title) and not is_empty(remarks) and not is_empty(command) and not is_empty(schedule):
            ret = jobmy_tables.insert_job(title, remarks, command, schedule)
            if ret:
                out["result"] = 0
            else:
                out["result"] = 1
                out["msg"] = "failed."
        else:
            out["result"] = 1
            out["msg"] = "Please input all params."
        self.write(json.dumps(out))
        logging.debug("job edit handler end.")
