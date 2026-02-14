#!/usr/bin/env python3
"""
Migration v9: Create test_cases table

This migration adds the test_cases table which is required for the
multi-test case judging system.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

def migrate():
    """Add test_cases table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Running migration v9: Creating test_cases table...")
    
    try:
        # Create test_cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                input TEXT NOT NULL,
                expected_output TEXT NOT NULL,
                is_sample BOOLEAN DEFAULT 0,
                points INTEGER DEFAULT 0,
                test_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_test_cases_problem_id 
            ON test_cases(problem_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_test_cases_is_sample 
            ON test_cases(problem_id, is_sample)
        ''')
        
        conn.commit()
        print("✓ test_cases table created successfully")
        print("✓ Indexes created")
        
        # Check if there are any problems without test cases
        problems = cursor.execute('SELECT id, title FROM problems').fetchall()
        if problems:
            print(f"\n⚠️  Found {len(problems)} problems without test cases")
            print("   You should upload test cases for each problem using the admin panel")
            print("   Or they will use the legacy test_input/expected_output fields")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\n✓ Migration v9 completed successfully!")

if __name__ == '__main__':
    migrate()
