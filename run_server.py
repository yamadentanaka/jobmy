import sys
import os
import time
import traceback
import tornado.web
import tornado.httpserver
import tornado.ioloop
import logging

import settings as jobmy_settings
from handlers import *
import job

logging.basicConfig(
    stream=sys.stdout,
    level=jobmy_settings.LOGGING_LEVEL,
    format="%(asctime)s %(levelname)s [%(filename)s(Line:%(lineno)d) [PID:%(process)d] [ThreadID:%(thread)d] %(message)s")

def start_job_watcher():
    try:
        logging.debug("start_job_watcher")
        # kill the long time jobs
        job.kill_jobs()
        # kick scheduled jobs
        job.kick_schedule_jobs()
    except Exception as ex:
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    logging.debug("start jobmy server.")
    if not os.path.exists(jobmy_settings.WORK_DIR):
        os.makedirs(jobmy_settings.WORK_DIR)
        logging.debug("create work directory.")
    settings = { 
        "template_path": os.path.join(os.getcwd(),  "templates"),
        "static_path": os.path.join(os.getcwd(),  "static"),
        "static_url_prefix": "/assets/",
    }
    app = tornado.web.Application([
            (r'/', TopHandler, {}),
            (r'/healthcheck', HealthCheckHandler, {}),
            (r'/job_edit', JobEditHandler, {}),
            (r'/job_execute', ExecuteJobHandler, {}),
            (r'/job_kill', KillJobHandler, {}),
            (r'/job_list', JobListHandler, {}),
            (r'/job_history_detail', JobHistoryDetailHandler, {}),
        ],  
        **settings
    )   
    server = tornado.httpserver.HTTPServer(app)
    server.bind(jobmy_settings.JOBMY_PORT)
    server.start(1)  # Specify number of subprocesses
    logging.debug("start jobmy job watcher.")
    tornado.ioloop.PeriodicCallback(start_job_watcher, jobmy_settings.JOB_CHECK_PERIOD).start()
    logging.debug("start jobmy web server.")
    tornado.ioloop.IOLoop.current().start()
