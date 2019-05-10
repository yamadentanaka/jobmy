import sys
import os
import time
import tornado.web
import tornado.httpserver
import tornado.ioloop
import logging

import settings as jobmy_settings
from handlers import *
import job

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(filename)s(Line:%(lineno)d) [PID:%(process)d] [ThreadID:%(thread)d] %(message)s")

def start_job_watcher():
    period = jobmy_settings.JOB_CHECK_PERIOD 
    ioloop = tornado.ioloop.IOLoop.current()
    ioloop.add_timeout(time.time() + period, start_job_watcher)
    # kill the long time jobs
    job.kill_jobs()
    # kick scheduled jobs
    job.kick_schedule_jobs()
    logging.debug("start_job_watcher")

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
            (r'/', TopHandler, dict()),
            (r'/healthcheck', HealthCheckHandler, dict()),
            (r'/job_edit', JobEditHandler, dict()),
            (r'/job_execute', ExecuteJobHandler, dict()),
            (r'/job_kill', KillJobHandler, dict()),
            (r'/job_list', JobListHandler, dict()),
            (r'/job_history_detail', JobHistoryDetailHandler, dict()),
        ],  
        **settings
    )   
    server = tornado.httpserver.HTTPServer(app)
    server.bind(8080)
    server.start(1)  # Specify number of subprocesses
    logging.debug("start jobmy web server.")
    start_job_watcher()
    logging.debug("start jobmy job watcher.")
    tornado.ioloop.IOLoop.current().start()
