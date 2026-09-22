# LibraryPro — Complete Setup Guide

> [!NOTE]
> **Architecture Update (SQLite & Python Migration)**:
> This project has been updated to use a fully database-driven architecture (Python + SQLite/MySQL). The C++ engine (`library.cpp`) mentioned in this documentation is **not required** for local execution or evaluation. The system operates fully using Python Flask and either local SQLite (`librarypro.db`) or MySQL databases.

## Project Architecture

```
LibraryPro/
├── backend/
│   ├── library.cpp          # C++ engine (all data structures)
│   ├── library             # Compiled binary (after build)
│   ├── library_data.dat    # Flat-file cache (auto-generated)
│   └── app.py              # Flask API + routes
│
├── frontend/
│   ├── static/
│   │   ├── css/style.css   # Full professional stylesheet (dark mode)
│   │   └── js/main.js      # Interactions, animations, dark mode
│   └── templates/
│       ├── base.html        # Sidebar + topbar layout
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html   # Charts + stat cards
│       ├── books.html       # Full CRUD + recommendations
│       ├── issue.html
│       ├── return.html
│       ├── queue.html       # Priority Queue visual
│       ├── stack.html       # Stack visual
│       ├── analytics.html   # 4 Chart.js charts
│       ├── students.html
│       ├── transactions.html
│       ├── profile.html
│       └── error.html
│
├── database/
│   └── schema.sql           # MySQL schema + seed data
│
├── docs/
│   └── SETUP.md             # This file
│
├── requirements.txt
├── Procfile                 # Render/Railway deployment
└── .env.example
```

---

## Data Structures Used (C++ Backend)

| Structure | C++ Type | Purpose |
|---|---|---|
| **Linked List** | Custom `Book*` | Core book catalog — O(n) traversal |
| **HashMap** | `unordered_map<int, Book*>` | O(1) book lookup by ID |
| **Stack** | `stack<pair<int,string>>` | Recent returns (LIFO) |
| **Queue** | `queue<pair<int,string>>` | Standard FIFO waiting list |
| **Priority Queue** | `priority_queue<WaitEntry, vector, greater<>>` | VIP/Faculty get served first |
| **Binary Search Tree** | Custom `BSTNode*` | Sorted display of books by title |
| **Graph** | `unordered_map<int, vector<int>>` | Book recommendation (adjacency list) |

---

## Step 1 — Prerequisites

Install these before anything else:

- **Python 3.10+**: https://python.org
- **MySQL 8.0+**: https://dev.mysql.com/downloads/
- **g++ compiler**: Usually pre-installed on Linux/macOS

On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install g++ mysql-server python3 python3-pip python3-venv
```

On macOS (Homebrew):
```bash
brew install gcc mysql python
```

On Windows:
- Install [MSYS2](https://www.msys2.org/) for g++
- Install [MySQL Installer](https://dev.mysql.com/downloads/installer/)

---

## Step 2 — Clone / Unzip the Project

```bash
# If you have the zip:
unzip LibraryPro.zip
cd LibraryPro
```

---

## Step 3 — Compile the C++ Engine

```bash
cd backend
g++ -O2 -std=c++17 library.cpp -o library
# On Windows: g++ -O2 -std=c++17 library.cpp -o library.exe
cd ..
```

Verify it works:
```bash
./backend/library help
```

---

## Step 4 — Set Up MySQL Database

```bash
# Log into MySQL
mysql -u root -p

# Run the schema
source database/schema.sql
# OR:
mysql -u root -p < database/schema.sql
```

This creates:
- Database: `librarypro`
- Tables: `users`, `books`, `transactions`, `queue`, `notifications`
- Seed data: admin account + 10 sample books

---

## Step 5 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:
```
SECRET_KEY=your-random-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DB=librarypro
```

---

## Step 6 — Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# Install packages
pip install -r requirements.txt
```

---

## Step 7 — Run the Application

```bash
# Make sure venv is active
cd backend
python app.py
```

Open your browser at: **http://localhost:5000**

### Default Login Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin@123` |
| Student | `john_doe` | `student123` |
| VIP Faculty | `prof_kumar` | `student123` |

---

## Step 8 — Generate Hashed Passwords (for new users)

The seed SQL file has pre-hashed passwords. To generate your own:

```python
import bcrypt
password = "your_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed)
# Paste this hash into the SQL INSERT or users table
```

---

## Deployment — Render.com

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn backend.app:app`
6. Add environment variables in Render dashboard
7. Add a MySQL plugin (or use Railway for DB)

## Deployment — Railway.app

1. Go to [railway.app](https://railway.app) → New Project
2. Deploy from GitHub repo
3. Add a MySQL plugin — Railway gives you the connection URL
4. Set env vars: `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
5. Railway auto-detects the Procfile

---

## API Endpoints Summary

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET/POST | `/login` | None | Login page |
| GET/POST | `/register` | None | Register |
| GET | `/dashboard` | User | Main dashboard |
| GET | `/books` | User | Book catalog |
| POST | `/add_book` | Admin | Add new book |
| POST | `/delete_book` | Admin | Delete book |
| GET/POST | `/issue` | User | Issue a book |
| GET/POST | `/return` | User | Return a book |
| GET | `/queue` | User | Waiting queue |
| GET | `/stack` | User | Return history |
| GET | `/analytics` | Admin | Charts & stats |
| GET | `/students` | Admin | Student list |
| GET | `/transactions` | Admin | All transactions |
| GET | `/profile` | User | My profile |
| GET | `/recommend/<id>` | User | AI recommendations |
| GET | `/api/stats` | User | JSON stats for charts |

---

## Troubleshooting

**"C++ binary not found"**
- Make sure you compiled with `g++` in the `backend/` directory
- On Windows, the binary is `library.exe` — update `CPP_BIN` in `app.py`

**"MySQL connection refused"**
- Check `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` in `.env`
- Run `mysql -u root -p` to test connection

**"ModuleNotFoundError: flask_mysqldb"**
- Make sure venv is activated: `source venv/bin/activate`
- Run `pip install -r requirements.txt` again

**Charts not showing**
- Charts require MySQL data. Issue a few books first.
- If MySQL is not connected, the dashboard gracefully shows a "Connect MySQL" placeholder.

**Dark mode not persisting**
- The theme is stored in `localStorage` — clear browser data if stuck.

---

## Feature Overview

| Feature | Status | Tech Used |
|---|---|---|
| CRUD (Add/Delete/View books) | ✅ | C++ Linked List + HashMap |
| Issue & Return | ✅ | C++ + MySQL transactions |
| Waiting Queue (VIP priority) | ✅ | C++ Priority Queue |
| Return History | ✅ | C++ Stack |
| Sorted Book Display | ✅ | C++ BST (in-order) |
| Book Recommendations | ✅ | C++ Graph (BFS) |
| Due Date & Fine System | ✅ | MySQL + Python |
| Auto-Assign on Return | ✅ | Queue + Notification |
| Analytics Dashboard | ✅ | Chart.js (4 charts) |
| Role-Based Auth | ✅ | bcrypt + Flask sessions |
| Dark Mode | ✅ | CSS variables + localStorage |
| Search & Filters | ✅ | C++ partial match |
| Pagination | ✅ | Python slice |
| Notifications | ✅ | MySQL + JS panel |
| Mobile Responsive | ✅ | CSS Grid + media queries |
| Deployment Ready | ✅ | Procfile + gunicorn |
