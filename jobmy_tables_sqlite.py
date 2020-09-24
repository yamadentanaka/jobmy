import logging
import traceback
from lib import sqlite_utils
import settings

# JOBS table functions
def get_all_jobs():
    query = "select * from JOBS where HOST = ? order by ID"
    try:
        return sqlite_utils.fetch_all(query, (settings.HOST_NAME,))
    except Exception as ex:
        logging.error(traceback.format_exc())
        return []

def insert_job(title, remarks, command, schedule, max_exec_time, next_job_ids, host_name):
    result = False
    query = "insert into JOBS (TITLE, REMARKS, COMMAND, SCHEDULE, MAX_EXEC_TIME, NEXT_JOB_IDS, HOST) values (?, ?, ?, ?, ?, ?, ?)"
    try:
        sqlite_utils.execute_query(query, (title, remarks, command, schedule, max_exec_time, next_job_ids, host_name))
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

def update_job(job_id, title, remarks, command, schedule, max_exec_time, next_job_ids, host_name):
    result = False
    query = "update JOBS set TITLE = ?, REMARKS = ?, COMMAND = ?, SCHEDULE = ?, MAX_EXEC_TIME = ?, NEXT_JOB_IDS = ?, HOST = ? where ID = ? and HOST = ?"
    try:
        sqlite_utils.execute_query(query, (title, remarks, command, schedule, max_exec_time, next_job_ids, host_name, job_id, settings.HOST_NAME))
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

def get_job_by_id(job_id):
    query = "select * from JOBS where ID = ? and HOST = ?"
    try:
        job = sqlite_utils.fetch_one(query, (job_id, settings.HOST_NAME))
        return job
    except Exception as ex:
        logging.error(traceback.format_exc())
    return None

# JOB_HISTORY table functions
def insert_job_history(value_dict):
    result = False
    query = "insert into JOB_HISTORY (JOB_ID, JOB_KEY, CALLER_JOB_KEY, COMMAND, HOST, IP_ADDRESS, PID, EXEC_RESULT, STD_OUT, STD_ERR, START_DATETIME, END_DATETIME) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    try:
        sqlite_utils.execute_query(query, (
            value_dict["JOB_ID"],
            value_dict["JOB_KEY"],
            value_dict["CALLER_JOB_KEY"] if "CALLER_JOB_KEY" in value_dict else None,
            value_dict["COMMAND"],
            value_dict["HOST"],
            value_dict["IP_ADDRESS"],
            value_dict["PID"],
            value_dict["EXEC_RESULT"] if "EXEC_RESULT" in value_dict else None,
            value_dict["STD_OUT"] if "STD_OUT" in value_dict else None,
            value_dict["STD_ERR"] if "STD_ERR" in value_dict else None,
            value_dict["START_DATETIME"] if "START_DATETIME" in value_dict else None,
            value_dict["END_DATETIME"] if "END_DATETIME" in value_dict else None
        ))
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

def update_job_history(value_dict):
    result = False
    query = "update JOB_HISTORY set RETURN_CODE = ?, EXEC_RESULT = ?, STD_OUT = ?, STD_ERR = ?, END_DATETIME = ? where JOB_KEY = ?"
    try:
        sqlite_utils.execute_query(query, (
            value_dict["RETURN_CODE"],
            value_dict["EXEC_RESULT"],
            value_dict["STD_OUT"],
            value_dict["STD_ERR"],
            value_dict["END_DATETIME"],
            value_dict["JOB_KEY"]
        ))
        result = True
    except Exception as ex:
        logging.error(traceback.format_exc())
    return result

def get_job_history_latest(num_records):
    query = "select h.ID, h.JOB_KEY, j.ID as JOB_ID, j.TITLE, h.HOST, h.IP_ADDRESS, h.EXEC_RESULT, h.START_DATETIME, h.END_DATETIME from JOBS j inner join JOB_HISTORY h on (j.ID = h.JOB_ID) where h.HOST = ? order by h.ID desc limit ?"
    result = []
    try:
        return sqlite_utils.fetch_all(query, (settings.HOST_NAME, num_records))
    except Exception as ex:
        logging.error(traceback.format_exc())
        return result

def get_job_history_by_job_id(job_id):
    query = "select \
        h.ID, \
        j.ID as JOB_ID, \
        j.TITLE, \
        j.REMARKS, \
        h.COMMAND, \
        j.SCHEDULE, \
        j.MAX_EXEC_TIME, \
        j.NEXT_JOB_IDS, \
        h.JOB_KEY, \
        h.CALLER_JOB_KEY, \
        h.HOST, \
        h.IP_ADDRESS, \
        h.PID, \
        h.RETURN_CODE, \
        h.EXEC_RESULT, \
        h.STD_OUT, \
        h.STD_ERR, \
        h.START_DATETIME, \
        h.END_DATETIME \
        from JOBS j inner join JOB_HISTORY h on (j.ID = h.JOB_ID) where h.ID = ? and j.HOST = ?"
    try:
        job = sqlite_utils.fetch_one(query, (job_id, settings.HOST_NAME))
        return job
    except Exception as ex:
        logging.error(traceback.format_exc())
    return None

def get_kill_target_jobs():
    query = "select h.ID, h.JOB_KEY, j.ID as JOB_ID, j.TITLE, h.PID \
            from JOBS j inner join JOB_HISTORY h on (j.ID = h.JOB_ID) \
            where h.EXEC_RESULT = 'running' and \
            j.MAX_EXEC_TIME > 0 and \
            strftime('%s', datetime('now', 'localtime')) - strftime('%s', h.START_DATETIME) > j.MAX_EXEC_TIME * 60 and \
            h.HOST = ?"
    result = []
    try:
        return sqlite_utils.fetch_all(query, (settings.HOST_NAME, ))
    except Exception as ex:
        logging.error(traceback.format_exc())
        return result

def get_running_jobs_by_id(job_id):
    query = "select h.ID, h.JOB_KEY, j.ID as JOB_ID, j.TITLE \
            from JOBS j inner join JOB_HISTORY h on (j.ID = h.JOB_ID) \
            where h.EXEC_RESULT = 'running' and \
            h.JOB_ID = ? and \
            h.HOST = ?"
    result = []
    try:
        return sqlite_utils.fetch_all(query, (job_id, settings.HOST_NAME))
    except Exception as ex:
        logging.error(traceback.format_exc())
        return result
