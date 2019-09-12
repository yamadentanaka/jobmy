import traceback
import logging
import sqlite3

import sys
import os
pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pardir)
import settings

def _get_connection():
    conn = sqlite3.connect(settings.SQLITE_FILE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_one(query, params):
    conn = None
    cur = None
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()
    except Exception as ex:
        logging.debug(traceback.format_exc())
        raise ex
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def fetch_all(query, params, func):
    conn = None
    cur = None
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        for row in cur.fetchall():
            func(row)
    except Exception as ex:
        logging.debug(traceback.format_exc())
        raise ex
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def execute_query(query, params, preprocess_query=None, preprocess_params=None):
    conn = None
    cur = None
    try:
        conn = _get_connection()
        cur = conn.cursor()
        if preprocess_query:
            if preprocess_params:
                cur.execute(preprocess_query, preprocess_params)
            else:
                cur.execute(preprocess_query)
        cur.execute(query, params)
        conn.commit()
    except Exception as ex:
        logging.debug(traceback.format_exc())
        raise ex
    finally:
        if cur:
            cur.close()
        if conn:
            conn.rollback()
            conn.close()

def execute_batch(query, param_array):
    conn = None
    cur = None
    try:
        conn = _get_connection()
        cur = conn.cursor()
        for params in param_array:
            cur.execute(query, params)
        conn.commit()
    except Exception as ex:
        logging.debug(traceback.format_exc())
        raise ex
    finally:
        if cur:
            cur.close()
        if conn:
            conn.rollback()
            conn.close()
