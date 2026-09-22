-- ============================================================
--  LibraryPro — MySQL Database Schema
--  Run this file once to initialise the database:
--    mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS librarypro
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE librarypro;

-- ─────────────────────────────────────────────
--  USERS TABLE (Admin + Students)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin','student') DEFAULT 'student',
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) UNIQUE,
    is_vip        TINYINT(1)   DEFAULT 0,   -- 1 = faculty/VIP
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────
--  BOOKS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS books (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    author        VARCHAR(100) NOT NULL,
    category      VARCHAR(80)  DEFAULT 'General',
    isbn          VARCHAR(20)  DEFAULT NULL,
    total_copies  INT          DEFAULT 1,
    available     INT          DEFAULT 1,
    description   TEXT         DEFAULT NULL,
    cover_url     VARCHAR(300) DEFAULT NULL,
    embedding     JSON         DEFAULT NULL,
    added_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_title    (title),
    INDEX idx_author   (author),
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────
--  TRANSACTIONS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT  NOT NULL,
    user_id      INT  NOT NULL,
    issue_date   DATE NOT NULL,
    due_date     DATE NOT NULL,
    return_date  DATE DEFAULT NULL,
    fine_amount  DECIMAL(8,2) DEFAULT 0.00,
    fine_paid    TINYINT(1)   DEFAULT 0,
    status       ENUM('active','returned','overdue') DEFAULT 'active',
    FOREIGN KEY (book_id) REFERENCES books(id)  ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE CASCADE,
    INDEX idx_status   (status),
    INDEX idx_due_date (due_date)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────
--  QUEUE TABLE (waiting list)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS queue (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    book_id     INT NOT NULL,
    user_id     INT NOT NULL,
    priority    INT DEFAULT 2,   -- 1=VIP, 2=Regular
    queued_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────
--  NOTIFICATIONS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    message     VARCHAR(300) NOT NULL,
    is_read     TINYINT(1)   DEFAULT 0,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────
--  REVIEWS TABLE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    book_id       INT NOT NULL,
    user_id       INT NOT NULL,
    rating        INT CHECK(rating BETWEEN 1 AND 5),
    review_text   TEXT,
    sentiment     VARCHAR(20) DEFAULT 'Neutral',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────────
--  SEED DATA
-- ─────────────────────────────────────────────

-- Admin account  (password: admin@123)
INSERT INTO users (username, password_hash, role, full_name, email, is_vip)
VALUES (
    'admin',
    '$2b$12$BpU4A5o7dBvROzpQkDEalubuBTp4LczYcXByMo/BCy7IS3cmKbVA2',
    'admin',
    'Library Admin',
    'admin@librarypro.edu',
    0
);

-- Demo student  (password: student123)
INSERT INTO users (username, password_hash, role, full_name, email, is_vip)
VALUES (
    'john_doe',
    '$2b$12$aa2M0aM5GKFSxsp9uPKq4.ezN5acSZoqPblll82pmP16iOgaKcIUa',
    'student',
    'John Doe',
    'john@student.edu',
    0
);

-- Demo VIP / faculty
INSERT INTO users (username, password_hash, role, full_name, email, is_vip)
VALUES (
    'prof_kumar',
    '$2b$12$T/FYGJvWEuu3kelff69eX.d.64e0JAdjiAmvy/N01cKTFLa/yzNPa',
    'student',
    'Prof. Ramesh Kumar',
    'rkumar@college.edu',
    1
);

-- Sample books
INSERT INTO books (title, author, category, isbn, total_copies, available, description) VALUES
('The C++ Programming Language', 'Bjarne Stroustrup', 'Programming', '978-0321563842', 3, 3, 'Definitive guide to C++ by its creator.'),
('Introduction to Algorithms', 'Cormen, Leiserson, Rivest, Stein', 'Computer Science', '978-0262033848', 2, 2, 'Comprehensive algorithms textbook (CLRS).'),
('Clean Code', 'Robert C. Martin', 'Programming', '978-0132350884', 2, 2, 'A handbook of agile software craftsmanship.'),
('Design Patterns', 'GoF', 'Software Engineering', '978-0201633610', 1, 1, 'Gang of Four classic design patterns.'),
('The Pragmatic Programmer', 'David Thomas', 'Programming', '978-0135957059', 2, 2, 'Your journey to mastery.'),
('Operating System Concepts', 'Silberschatz, Galvin', 'Computer Science', '978-1119800361', 3, 3, 'Standard OS textbook.'),
('Database System Concepts', 'Silberschatz', 'Database', '978-0078022159', 2, 2, 'Authoritative DB reference.'),
('Computer Networks', 'Andrew Tanenbaum', 'Networking', '978-0132126953', 2, 2, 'Top-down approach to networks.'),
('Artificial Intelligence', 'Russell & Norvig', 'AI/ML', '978-0134610993', 2, 2, 'Modern approach to AI.'),
('Python Crash Course', 'Eric Matthes', 'Programming', '978-1593279288', 3, 3, 'Fast-paced intro to Python.');
