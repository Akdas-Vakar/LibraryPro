import os

import sqlite3

import mysql.connector

from datetime import datetime, date

def curdate():

    return date.today().isoformat()

def datediff(d1, d2):

    try:

        if not d1 or not d2:

            return 0

        if isinstance(d1, str):

            dt1 = datetime.strptime(d1.split()[0], "%Y-%m-%d").date()

        else:

            dt1 = d1

        if isinstance(d2, str):

            dt2 = datetime.strptime(d2.split()[0], "%Y-%m-%d").date()

        else:

            dt2 = d2

        return (dt1 - dt2).days

    except Exception:

        return 0

class SQLiteCursorWrapper:

    def __init__(self, cursor):

        self.cursor = cursor

    def execute(self, sql, params=None):

        sql = sql.replace('%s', '?')

        sql = sql.replace("DATE_SUB(CURDATE(),INTERVAL 14 DAY)", "date('now', '-14 days')")

        sql = sql.replace("DATE_SUB(CURDATE(), INTERVAL 14 DAY)", "date('now', '-14 days')")

        sql = sql.replace("DATE_SUB(CURDATE(),INTERVAL 7 DAY)", "date('now', '-7 days')")

        sql = sql.replace("DATE_SUB(CURDATE(), INTERVAL 7 DAY)", "date('now', '-7 days')")

        if 'SET FOREIGN_KEY_CHECKS' in sql:

            if '0' in sql:

                sql = "PRAGMA foreign_keys = OFF"

            else:

                sql = "PRAGMA foreign_keys = ON"

        if 'TRUNCATE TABLE' in sql:

            table_name = sql.split('TRUNCATE TABLE')[1].strip(' ;')

            sql = f"DELETE FROM {table_name}"

        if params is not None:

            if not isinstance(params, (tuple, list)):

                params = (params,)

            self.cursor.execute(sql, params)

        else:

            self.cursor.execute(sql)

    def fetchall(self):

        return self.cursor.fetchall()

    def fetchone(self):

        return self.cursor.fetchone()

    def close(self):

        self.cursor.close()

    @property

    def lastrowid(self):

        return self.cursor.lastrowid

class SQLiteConnectionWrapper:

    def __init__(self, conn):

        self.conn = conn

    def cursor(self, dictionary=False):

        if dictionary:

            self.conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

        else:

            self.conn.row_factory = None

        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):

        self.conn.commit()

    def close(self):

        self.conn.close()

def init_sqlite_db(db_path):

    print(f"[SQLite] Initializing database at {db_path}...")

    conn = sqlite3.connect(db_path)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    schema_path = os.path.abspath(os.path.join(current_dir, '..', 'database', 'schema_sqlite.sql'))

    if not os.path.exists(schema_path):

        print(f"[SQLite] Error: Schema file not found at {schema_path}")

        return

    with open(schema_path, 'r', encoding='utf-8') as f:

        sql_script = f.read()

    conn.executescript(sql_script)

    conn.commit()

    conn.close()

    print("[SQLite] Database initialized successfully.")

def get_db():

    db_type = os.environ.get('DB_TYPE', '').lower()

    use_sqlite = (db_type == 'sqlite') or not db_type

    if not use_sqlite:

        try:

            DB_CFG = {

                'host':     os.environ.get('MYSQL_HOST',     'localhost'),

                'user':     os.environ.get('MYSQL_USER',     'root'),

                'password': os.environ.get('MYSQL_PASSWORD', '1234'),

                'database': os.environ.get('MYSQL_DB',       'librarypro'),

            }

            return mysql.connector.connect(**DB_CFG)

        except Exception as e:

            print(f"[Database] Failed to connect to MySQL: {e}. Falling back to SQLite.")

            use_sqlite = True

    if use_sqlite:

        current_dir = os.path.dirname(os.path.abspath(__file__))

        db_path = os.path.abspath(os.path.join(current_dir, '..', 'librarypro.db'))

        db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 0

        if not db_exists:

            init_sqlite_db(db_path)

        conn = sqlite3.connect(db_path)

        conn.create_function("CURDATE", 0, curdate)

        conn.create_function("DATEDIFF", 2, datediff)

        return SQLiteConnectionWrapper(conn)

