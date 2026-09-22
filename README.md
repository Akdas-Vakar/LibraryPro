# AI-Powered Library Management System

An intelligent library management system built with Python, Flask, and MySQL/SQLite using advanced data structures and Gemini AI for efficient book and student management.

> [!TIP]
> **🚀 Quick Start for Evaluators (Zero-Config SQLite Setup)**
> 
> To run and evaluate this application locally without installing a MySQL database server:
> 
> 1. **Prerequisites**: Python 3.7+ (with pip)
> 2. **Install Dependencies**:
>    ```bash
>    pip install -r requirements.txt
>    ```
> 3. **Seed SQLite Database**: (Creates `librarypro.db` and populates the 100 catalog books and default users):
>    ```bash
>    python seed_books.py
>    ```
> 4. **Run the App**:
>    ```bash
>    python app.py
>    ```
> 5. **Test in Browser**: Open **[http://localhost:5000](http://localhost:5000)**
>    * **Admin / Librarian Login**: `admin` / `admin123`
>    * **Student Login**: `john_doe` / `student123`


## 📋 Features

- **Student Management**: Register, manage student profiles, and track borrowing history
- **Book Management**: Maintain comprehensive book catalog with details and availability status
- **Book Borrowing/Return**: Handle book issuance and returns with automatic tracking
- **Queue Management**: Track waiting queues for popular books
- **Issue Tracking**: Monitor and resolve library-related issues
- **Analytics Dashboard**: View library statistics and usage patterns
- **AI-Powered Assistant**: Natural language chatbot, reviews sentiment tagging, and book summaries powered by Gemini 3.1 Flash.
- **User Authentication**: Secure login system for students and librarians

## 🛠️ Tech Stack

- **Backend**: Python 3.x with Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MySQL (Local / Railway)
- **AI Engine**: Gemini API (`gemini-3.1-flash-lite`, `gemini-embedding-2`)
- **Deployment**: Heroku-ready (Procfile included)

## 📁 Project Structure

```
LibraryPro/
├── backend/                 # Backend Python scripts
│   ├── app.py              # Flask application
│   ├── ai_utils.py         # Gemini AI helper functions (Chatbot, Sentiment, Summaries)
│   ├── fix_login.py        # Login functionality
│   └── sync_books.py       # Book synchronization
├── frontend/
│   ├── static/             # CSS and JavaScript files
│   │   ├── css/
│   │   └── js/
│   └── templates/          # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── books.html
│       ├── students.html
│       ├── issue.html
│       ├── return.html
│       ├── queue.html
│       ├── analytics.html
│       ├── profile.html
│       ├── error.html
│       ├── stack.html
│       └── transactions.html
├── database/               # Database schema
│   └── schema.sql
├── docs/                   # Documentation
│   └── SETUP.md
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── Procfile               # Heroku deployment config
├── setup_windows.bat      # Windows setup script
└── setup_windows.ps1      # Windows PowerShell setup script
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)
- SQLite3 or MySQL
- Git

### Installation

#### Windows (PowerShell)

```powershell
# Run the setup script
.\setup_windows.ps1
```

#### Windows (Batch)

```batch
setup_windows.bat
```

#### Manual Setup

1. **Clone the repository**
   ```bash
    git clone <your-repository-url>
    cd LibraryPro
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Linux/macOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database**
   - Install MySQL and log in to your server.
   - Run the schema script to create the tables and database:
     ```bash
     mysql -u root -p < database/schema.sql
     ```

6. **Seed the 100 books catalog**
   - Run the seeding script to populate the books and generate vector embeddings (if `GEMINI_API_KEY` is set):
     ```bash
     python seed_books.py
     ```

7. **Run the application**
   - Run the Flask development server:
     ```bash
     python backend/app.py
     ```

   The application will start at `http://localhost:5000`

## 📖 Usage

### Student Portal
- **Register**: Create new student account
- **Login**: Access personal dashboard
- **Browse Books**: View available books in catalog
- **Borrow Books**: Issue books to your account
- **Return Books**: Return borrowed books
- **View History**: Check transaction history and profile

### Librarian Features
- **Dashboard**: View system statistics and analytics
- **Student Management**: Manage student records
- **Book Management**: Add, edit, or remove books
- **Issue Resolution**: Track and resolve library issues
- **Queue Management**: Monitor book waiting queues

## 🔧 Configuration

Key configuration files:
- `backend/app.py` - Flask app configuration
- `database/schema.sql` - Database schema
- `requirements.txt` - Python dependencies

## 📊 Advanced Features

- **Efficient Search**: Optimized using keyword-based and vector-based semantic search
- **Queue Management**: Priority-based queue system for book reservations
- **Analytics Dashboard**: Real-time insights on library usage
- **Transaction History**: Complete audit trail of all transactions

## 🚢 Deployment

The project includes a `Procfile` for easy deployment on Heroku:

```bash
git push heroku main
```

## 📝 API Endpoints

Key endpoints include:
- `POST /login` - Student/Librarian login
- `POST /register` - Student registration
- `GET /books` - List available books
- `POST /borrow` - Borrow a book
- `POST /return` - Return a book
- `GET /dashboard` - View dashboard
- `GET /analytics` - View analytics

## 🐛 Troubleshooting

- **Module not found**: Ensure virtual environment is activated and dependencies are installed
- **Database errors**: Check `database/schema.sql` and verify database connection
- **Port already in use**: Change port in `app.py` or kill the process using port 5000

## 📚 Documentation

See [SETUP.md](docs/SETUP.md) for detailed setup instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.


