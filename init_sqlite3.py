import sqlite3
from lib import sqlite_utils

if __name__ == "__main__":
    query_file = "./sql/remake_sqlite3.sql"
    with open(query_file, "r") as fp:
        all_query = fp.read()
    for query in all_query.split(";\n"):
        # print(query)
        sqlite_utils.execute_query(query, ())
