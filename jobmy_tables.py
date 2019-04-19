import logging
import traceback
from lib import mysql_utils

def get_all_jobs():
    query = "select * from JOBS order by ID"
    result = []
    def __inner_select_func(row):
        result.append(row)
    try:
        mysql_utils.fetch_all(query, None, __inner_select_func)
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

def insert_job(title, remarks, command, schedule):
    result = False
    query = "insert into JOBS (TITLE, REMARKS, COMMAND, SCHEDULE) values (%s, %s, %s, %s)"
    try:
        mysql_utils.execute_query(query, [title, remarks, command, schedule])
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result
