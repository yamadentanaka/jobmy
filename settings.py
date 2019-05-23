import os
import socket

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = ""
MYSQL_PASSWORD = ""
MYSQL_DB_NAME = "JOBMY"
MYSQL_CHARSET = "utf8"

WORK_DIR = "./tmp_jobmy"

HOST_NAME = os.environ.get("JOBMY_HOST_NAME", socket.gethostname())

JOB_CHECK_PERIOD = 3

SLACK_WEBHOOK_URL = ""
SLACK_SEND_CHANNEL = ""
