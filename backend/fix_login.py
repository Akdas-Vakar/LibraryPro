import os

import sys

import bcrypt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_helper import get_db

conn = get_db()

cur = conn.cursor()

h = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()

cur.execute("DELETE FROM users WHERE username='admin'")

cur.execute("""

    INSERT INTO users (username, password_hash, role, full_name, email, is_vip)

    VALUES ('admin', %s, 'admin', 'Library Admin', 'admin@lib.com', 0)

""", (h,))

h2 = bcrypt.hashpw(b'student123', bcrypt.gensalt()).decode()

cur.execute("DELETE FROM users WHERE username='john_doe'")

cur.execute("""

    INSERT INTO users (username, password_hash, role, full_name, email, is_vip)

    VALUES ('john_doe', %s, 'student', 'John Doe', 'john@student.com', 0)

""", (h2,))

conn.commit()

cur.close()

conn.close()

print("All done!")

print("Login: admin / admin123")

print("Login: john_doe / student123")

