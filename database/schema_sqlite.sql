-- SQLite Schema for LibraryPro

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT DEFAULT 'student',
    full_name     TEXT NOT NULL,
    email         TEXT UNIQUE,
    is_vip        INTEGER DEFAULT 0,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT NOT NULL,
    author        TEXT NOT NULL,
    category      TEXT DEFAULT 'General',
    isbn          TEXT DEFAULT NULL,
    total_copies  INTEGER DEFAULT 1,
    available     INTEGER DEFAULT 1,
    description   TEXT DEFAULT NULL,
    cover_url     TEXT DEFAULT NULL,
    embedding     TEXT DEFAULT NULL, -- Stored as JSON string
    added_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    slot_id       INTEGER DEFAULT NULL,
    library       TEXT DEFAULT NULL,
    floor         TEXT DEFAULT NULL,
    section       TEXT DEFAULT NULL,
    bookcase      TEXT DEFAULT NULL,
    shelf         TEXT DEFAULT NULL,
    slot          TEXT DEFAULT NULL,
    location_code TEXT DEFAULT NULL,
    volume_number TEXT DEFAULT NULL,
    rfid_tag      TEXT DEFAULT NULL,
    barcode       TEXT DEFAULT NULL,
    temporarily_off_shelf INTEGER DEFAULT 0,
    FOREIGN KEY (slot_id) REFERENCES locations_slot(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS locations_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS locations_floor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    FOREIGN KEY (library_id) REFERENCES locations_library(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations_section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    FOREIGN KEY (floor_id) REFERENCES locations_floor(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations_bookcase (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    FOREIGN KEY (section_id) REFERENCES locations_section(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations_shelf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bookcase_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    FOREIGN KEY (bookcase_id) REFERENCES locations_bookcase(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations_slot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shelf_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    FOREIGN KEY (shelf_id) REFERENCES locations_shelf(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inventory_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);

CREATE TABLE IF NOT EXISTS transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id      INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    issue_date   TEXT NOT NULL,
    due_date     TEXT NOT NULL,
    return_date  TEXT DEFAULT NULL,
    fine_amount  DECIMAL(8,2) DEFAULT 0.00,
    fine_paid    INTEGER DEFAULT 0,
    status       TEXT DEFAULT 'active',
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_due_date ON transactions(due_date);

CREATE TABLE IF NOT EXISTS queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    priority    INTEGER DEFAULT 2, -- 1=VIP, 2=Regular
    queued_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    message     TEXT NOT NULL,
    is_read     INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reviews (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id       INTEGER NOT NULL,
    user_id       INTEGER NOT NULL,
    rating        INTEGER CHECK(rating BETWEEN 1 AND 5),
    review_text   TEXT,
    sentiment     TEXT DEFAULT 'Neutral',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Seed Data
INSERT OR IGNORE INTO users (id, username, password_hash, role, full_name, email, is_vip)
VALUES (1, 'admin', '$2b$12$BpU4A5o7dBvROzpQkDEalubuBTp4LczYcXByMo/BCy7IS3cmKbVA2', 'admin', 'Library Admin', 'admin@librarypro.edu', 0);

INSERT OR IGNORE INTO users (id, username, password_hash, role, full_name, email, is_vip)
VALUES (2, 'john_doe', '$2b$12$aa2M0aM5GKFSxsp9uPKq4.ezN5acSZoqPblll82pmP16iOgaKcIUa', 'student', 'John Doe', 'john@student.edu', 0);

INSERT OR IGNORE INTO users (id, username, password_hash, role, full_name, email, is_vip)
VALUES (3, 'prof_kumar', '$2b$12$T/FYGJvWEuu3kelff69eX.d.64e0JAdjiAmvy/N01cKTFLa/yzNPa', 'student', 'Prof. Ramesh Kumar', 'rkumar@college.edu', 1);

INSERT OR IGNORE INTO books (id, title, author, category, isbn, total_copies, available, description) VALUES
(1, 'The C++ Programming Language', 'Bjarne Stroustrup', 'Programming', '978-0321563842', 3, 3, 'Definitive guide to C++ by its creator.'),
(2, 'Introduction to Algorithms', 'Cormen, Leiserson, Rivest, Stein', 'Computer Science', '978-0262033848', 2, 2, 'Comprehensive algorithms textbook (CLRS).'),
(3, 'Clean Code', 'Robert C. Martin', 'Programming', '978-0132350884', 2, 2, 'A handbook of agile software craftsmanship.'),
(4, 'Design Patterns', 'GoF', 'Software Engineering', '978-0201633610', 1, 1, 'Gang of Four classic design patterns.'),
(5, 'The Pragmatic Programmer', 'David Thomas', 'Programming', '978-0135957059', 2, 2, 'Your journey to mastery.'),
(6, 'Operating System Concepts', 'Silberschatz, Galvin', 'Computer Science', '978-1119800361', 3, 3, 'Standard OS textbook.'),
(7, 'Database System Concepts', 'Silberschatz', 'Database', '978-0078022159', 2, 2, 'Authoritative DB reference.'),
(8, 'Computer Networks', 'Andrew Tanenbaum', 'Networking', '978-0132126953', 2, 2, 'Top-down approach to networks.'),
(9, 'Artificial Intelligence', 'Russell & Norvig', 'AI/ML', '978-0134610993', 2, 2, 'Modern approach to AI.'),
(10, 'Python Crash Course', 'Eric Matthes', 'Programming', '978-1593279288', 3, 3, 'Fast-paced intro to Python.');
