#!/usr/bin/env python3
"""
Database migration script to add new columns for Phase 1 features.
Run this to update existing database without losing data.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

def migrate_database():
    """Add new columns to existing tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Add enabled column to problems table
    try:
        cursor.execute('ALTER TABLE problems ADD COLUMN enabled INTEGER DEFAULT 1')
        print("✓ Added 'enabled' column to problems table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("✓ 'enabled' column already exists in problems table")
        else:
            raise
    
    # Add created_at column to problems table
    try:
        # SQLite doesn't support CURRENT_TIMESTAMP in ALTER TABLE
        # Use NULL and update existing rows
        cursor.execute('ALTER TABLE problems ADD COLUMN created_at TIMESTAMP')
        cursor.execute("UPDATE problems SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
        print("✓ Added 'created_at' column to problems table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("✓ 'created_at' column already exists in problems table")
        else:
            raise
    
    # Add judging_status column to submissions table
    try:
        cursor.execute("ALTER TABLE submissions ADD COLUMN judging_status TEXT")
        cursor.execute("UPDATE submissions SET judging_status = 'completed' WHERE judging_status IS NULL")
        print("✓ Added 'judging_status' column to submissions table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("✓ 'judging_status' column already exists in submissions table")
        else:
            raise
    
    conn.commit()
    conn.close()
    
    print("\n✓ Database migration completed successfully!")
    print("Your existing data is preserved.")

if __name__ == '__main__':
    migrate_database()
