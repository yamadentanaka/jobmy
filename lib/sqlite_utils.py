import traceback
import logging
import sqlite3
import contextlib

import sys
import os
pardir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pardir)
import settings


@contextlib.contextmanager
def _get_cursor():
    conn = None
    cur = None
    try:
        conn = sqlite3.connect(settings.SQLITE_FILE_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        yield cur
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def fetch_one(query, params):
    with _get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()


def fetch_all(query, params):
    with _get_cursor() as cur:
        cur.execute(query, params)
        for row in cur.fetchall():
            yield row


def execute_query(query, params, preprocess_query=None, preprocess_params=None):
    with _get_cursor() as cur:
        if preprocess_query:
            if preprocess_params:
                cur.execute(preprocess_query, preprocess_params)
            else:
                cur.execute(preprocess_query)
        cur.execute(query, params)
        cur.connection.commit()


def execute_batch(query, param_array):
    with _get_cursor() as cur:
        for params in param_array:
            cur.execute(query, params)
        cur.connection.commit()
