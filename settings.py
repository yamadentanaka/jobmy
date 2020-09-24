import os
import socket
import logging

LOGGING_LEVEL = logging.DEBUG

WORK_DIR = "./tmp_jobmy"
JOBMY_PORT = 8080
HOST_NAME = os.environ.get("JOBMY_HOST_NAME", socket.gethostname())
JOB_CHECK_PERIOD = 1000

SLACK_WEBHOOK_URL = ""
SLACK_SEND_CHANNEL = ""

# DB_TYPE = "MySQL"
DB_TYPE = "SQLite"

# MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = ""
MYSQL_PASSWORD = ""
MYSQL_DB_NAME = "JOBMY"
MYSQL_CHARSET = "utf8"

# SQLite
SQLITE_FILE_PATH = "./jobmy.sqlite3"
