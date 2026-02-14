#!/usr/bin/env python3
"""
Migration v10: Add missing columns to problems table

Adds total_marks and constraints columns if they don't exist.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

def column_exists(cursor, table, column):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def migrate():
    """Add missing columns to problems table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Running migration v10: Adding missing columns to problems table...")
    
    try:
        # Add total_marks column if it doesn't exist
        if not column_exists(cursor, 'problems', 'total_marks'):
            cursor.execute('ALTER TABLE problems ADD COLUMN total_marks INTEGER DEFAULT 100')
            print("✓ Added total_marks column")
        else:
            print("✓ total_marks column already exists")
        
        # Add constraints column if it doesn't exist
        if not column_exists(cursor, 'problems', 'constraints'):
            cursor.execute('ALTER TABLE problems ADD COLUMN constraints TEXT')
            print("✓ Added constraints column")
        else:
            print("✓ constraints column already exists")
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\n✓ Migration v10 completed successfully!")

if __name__ == '__main__':
    migrate()
