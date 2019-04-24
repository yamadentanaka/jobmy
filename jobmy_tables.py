import logging
import traceback
from lib import mysql_utils

# JOBS table functions
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

def get_job_by_id(job_id):
    query = "select * from JOBS where ID = %s"
    try:
        job = mysql_utils.fetch_one(query, [job_id])
        return job
    except Exception as ex:
        logging.error(traceback.format_exc())
    return None

def update_job_last_exec(job_id, state, last_exec_result, last_exec_datetime):
    result = False
    query = "update JOBS set STATE = %s, LAST_EXEC_RESULT = %s, LAST_EXEC_DATETIME = %s where JOB_ID = %s"
    try:
        mysql_utils.execute_query(query, [state, last_exec_result, last_exec_datetime, job_id])
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

# JOB_HISTORY table functions
def insert_job_history(value_dict):
    result = False
    query = "insert into JOB_HISTORY (JOB_ID, JOB_KEY, HOST, PID, EXEC_RESULT, STD_OUT, STD_ERR, START_DATETIME, END_DATETIME) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        mysql_utils.execute_query(query, [
            value_dict["JOB_ID"],
            value_dict["JOB_KEY"],
            value_dict["HOST"],
            value_dict["PID"],
            value_dict["EXEC_RESULT"] if "EXEC_RESULT" in value_dict else None,
            value_dict["STD_OUT"] if "STD_OUT" in value_dict else None,
            value_dict["STD_ERR"] if "STD_ERR" in value_dict else None,
            value_dict["START_DATETIME"] if "START_DATETIME" in value_dict else None,
            value_dict["END_DATETIME"] if "END_DATETIME" in value_dict else None
        ])
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

def update_job_history(value_dict):
    result = False
    query = "update JOB_HISTORY set EXEC_RESULT = %s, STD_OUT = %s, STD_ERR = %s, END_DATETIME = %s where JOB_KEY = %s"
    try:
        mysql_utils.execute_query(query, [
            value_dict["EXEC_RESULT"],
            value_dict["STD_OUT"],
            value_dict["STD_ERR"],
            value_dict["END_DATETIME"],
            value_dict["JOB_KEY"]
        ])
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result
