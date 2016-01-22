import os
import psycopg2

CONN = None

def db_connection():
    global CONN
    if not CONN:
        CONN = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (
            os.environ["DB_NAME"],
            os.environ["DB_USER"],
            os.environ["DB_HOST"],
            os.environ["DB_PASS"]))
    return CONN
    
def execute(str):
    cur = db_connection().cursor()
    cur.execute(str)
    return cur
    
def close_connection():
    db_connection().close()