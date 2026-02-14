#!/usr/bin/env python3
"""
Migration v7: Add total_marks column and remove round_number, difficulty
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

def migrate():
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()
    
    print("Running migration v7...")
    
    # Check if total_marks column exists
    cursor.execute("PRAGMA table_info(problems)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'total_marks' not in columns:
        print("Adding total_marks column...")
        cursor.execute('ALTER TABLE problems ADD COLUMN total_marks INTEGER DEFAULT 100')
        print("✓ Added total_marks column")
    else:
        print("✓ total_marks column already exists")
    
    # Note: SQLite doesn't support DROP COLUMN easily, so we'll just leave
    # round_number and difficulty columns if they exist. They won't be used.
    
    conn.commit()
    conn.close()
    print("Migration v7 complete!")

if __name__ == '__main__':
    migrate()
