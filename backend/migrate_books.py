import sqlite3

def migrate():

    conn = sqlite3.connect('../librarypro.db')

    cur = conn.cursor()

    try:

        cur.execute("ALTER TABLE books ADD COLUMN publication_year INTEGER DEFAULT NULL")

        print("Added publication_year")

    except Exception as e:

        print("publication_year error:", e)

    try:

        cur.execute("ALTER TABLE books ADD COLUMN publisher TEXT DEFAULT NULL")

        print("Added publisher")

    except Exception as e:

        print("publisher error:", e)

    conn.commit()

    conn.close()

    print("Migration complete.")

if __name__ == '__main__':

    migrate()

