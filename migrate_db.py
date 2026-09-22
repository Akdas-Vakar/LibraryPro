import sqlite3
import os

def migrate():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'librarypro.db'))
    print(f"Migrating database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    
    queries = [
        """
        CREATE TABLE IF NOT EXISTS locations_floor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS locations_section (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            floor_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            FOREIGN KEY (floor_id) REFERENCES locations_floor(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS locations_module (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            FOREIGN KEY (section_id) REFERENCES locations_section(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS locations_shelf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            FOREIGN KEY (module_id) REFERENCES locations_module(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS locations_slot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shelf_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            FOREIGN KEY (shelf_id) REFERENCES locations_shelf(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS inventory_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        );
        """
    ]
    
    for q in queries:
        cur.execute(q)
        
    
    
    new_columns = [
        ("slot_id", "INTEGER DEFAULT NULL REFERENCES locations_slot(id)"),
        ("floor", "TEXT DEFAULT NULL"),
        ("section", "TEXT DEFAULT NULL"),
        ("module", "TEXT DEFAULT NULL"),
        ("shelf", "TEXT DEFAULT NULL"),
        ("slot", "TEXT DEFAULT NULL"),
        ("location_code", "TEXT DEFAULT NULL"),
        ("temporarily_off_shelf", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_def in new_columns:
        try:
            cur.execute(f"ALTER TABLE books ADD COLUMN {col_name} {col_def}")
            print(f"Added column {col_name} to books.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_name} already exists.")
            else:
                raise e
                
    
    cur.execute("SELECT id FROM locations_floor WHERE code = 'F1'")
    floor = cur.fetchone()
    if not floor:
        cur.execute("INSERT INTO locations_floor (name, code) VALUES ('First Floor', 'F1')")
        f_id = cur.lastrowid
        cur.execute("INSERT INTO locations_section (floor_id, name, code) VALUES (?, 'Default Section', 'SEC1')", (f_id,))
        s_id = cur.lastrowid
        cur.execute("INSERT INTO locations_module (section_id, name, code) VALUES (?, 'Default Module M01', 'M01')", (s_id,))
        m_id = cur.lastrowid
        cur.execute("INSERT INTO locations_shelf (module_id, name, code) VALUES (?, 'Default Shelf S1', 'S1')", (m_id,))
        sh_id = cur.lastrowid
        cur.execute("INSERT INTO locations_slot (shelf_id, name, code) VALUES (?, 'Default Slot A', 'A')", (sh_id,))
        sl_id = cur.lastrowid
        
        
        cur.execute("""
            UPDATE books 
            SET slot_id = ?, floor = 'First Floor', section = 'Default Section', module = 'Default Module M01', 
                shelf = 'Default Shelf S1', slot = 'Default Slot A', location_code = 'F1-SEC1-M01-S1-A'
            WHERE slot_id IS NULL
        """, (sl_id,))
        print("Created default location and assigned to existing books.")
        
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_books_location_code ON books(location_code)")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
