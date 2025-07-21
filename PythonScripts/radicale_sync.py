#jfr
import sys, psycopg2, requests
from utils import DB, RAD

def create_user_accounts():
    db_connection = psycopg2.connect(**DB)
    db_cursor = db_connection.cursor()
    db_cursor.execute("select * from users;")
    users = db_cursor.fetchall()

    session = requests.Session()
    session.auth = (RAD_USER, RAD_PASS)
    for user in users:
        pass  