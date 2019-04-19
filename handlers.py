import tornado.web
import logging
import traceback

import jobmy_tables

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
        self.render("job_edit.html")
        logging.debug("job edit handler end.")

    def post(self):
        logging.debug("job edit handler start.")
        title = self.get_argument("title", None)
        remarks = self.get_argument("remarks", None)
        command = self.get_argument("command", None)
        schedule = self.get_argument("schedule", None)
        if title is not None and remarks is not None and command is not None and schedule is not None:
            ret = jobmy_tables.insert_job(title, remarks, command, schedule)
            if ret:
                msg = "OK"
            else:
                msg = "登録に失敗しました。"
            self.render("job_edit.html", msg=msg)
        else:
            msg = "全ての項目を入力するしてください。"
            self.render("job_edit.html", msg=msg)
        logging.debug("job edit handler end.")
