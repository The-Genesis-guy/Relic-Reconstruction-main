#!/usr/bin/env python3
import sqlite3
import os
import hashlib
import sys

# Add current directory to path to import config
sys.path.append(os.getcwd())
try:
    import config
except ImportError:
    print("Error: config.py not found in current directory.")
    sys.exit(1)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_database():
    db_path = config.DB_NAME
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Initializing database at: {db_path}")
    
    # 1. Create Tables
    print("Creating tables...")
    
    # Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL, 
        role TEXT DEFAULT 'user', 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        session_token TEXT
    )''')
    
    # Contests
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        show_leaderboard BOOLEAN DEFAULT 1
    )''')
    
    # Problems
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT NOT NULL, 
        description TEXT NOT NULL, 
        input_format TEXT NOT NULL, 
        output_format TEXT NOT NULL, 
        sample_input TEXT NOT NULL, 
        sample_output TEXT NOT NULL, 
        test_input TEXT NOT NULL, 
        expected_output TEXT NOT NULL, 
        enabled INTEGER DEFAULT 1, 
        created_at TIMESTAMP, 
        problem_type TEXT DEFAULT 'coding', 
        contest_id INTEGER REFERENCES contests(id), 
        starter_code TEXT, 
        round_number INTEGER DEFAULT 1, 
        problem_mode TEXT DEFAULT 'stdin', 
        function_name TEXT DEFAULT 'solve', 
        difficulty TEXT DEFAULT 'easy', 
        reference_solution TEXT, 
        total_marks INTEGER DEFAULT 100, 
        constraints TEXT DEFAULT ''
    )''')
    
    # Submissions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        problem_id INTEGER NOT NULL, 
        code TEXT NOT NULL, 
        language TEXT NOT NULL, 
        output TEXT, 
        verdict TEXT, 
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        judging_status TEXT DEFAULT 'pending', 
        points_awarded INTEGER DEFAULT 0, 
        contest_id INTEGER REFERENCES contests(id), 
        tests_passed INTEGER DEFAULT 0, 
        tests_total INTEGER DEFAULT 0, 
        FOREIGN KEY (user_id) REFERENCES users(id), 
        FOREIGN KEY (problem_id) REFERENCES problems(id)
    )''')
    
    # Test Cases
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        problem_id INTEGER NOT NULL, 
        input TEXT NOT NULL, 
        expected_output TEXT NOT NULL, 
        points INTEGER DEFAULT 10, 
        is_sample BOOLEAN DEFAULT 0, 
        description TEXT, 
        test_order INTEGER DEFAULT 0, 
        FOREIGN KEY (problem_id) REFERENCES problems(id)
    )''')
    
    # Settings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    
    # Admin Logs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES users(id)
    )''')
    
    # Problem Code (for multiple language support)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS problem_code (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        solution_code TEXT,
        starter_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems(id),
        UNIQUE(problem_id, language)
    )''')

    # 2. Setup Indices
    print("Creating indices...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_user_problem ON submissions(user_id, problem_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_contest ON submissions(contest_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_problems_contest ON problems(contest_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(judging_status)")

    # 3. Insert Default Settings
    print("Inserting default settings...")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('leaderboard_enabled', '1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('show_scores_to_students', '1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('show_difficulty_to_students', '1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('contest_title', 'Relic Reconstruction 2026')")

    # 4. Create Default Admin
    print("Creating default admin account...")
    admin_user = "admin"
    admin_pass = hash_password("RelicAdmin!2026")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                   (admin_user, admin_pass, "admin"))

    conn.commit()
    conn.close()
    print("\n✓ Database initialized successfully!")
    print("Admin Portal: use 'admin' / 'RelicAdmin!2026'")

if __name__ == '__main__':
    init_database()
