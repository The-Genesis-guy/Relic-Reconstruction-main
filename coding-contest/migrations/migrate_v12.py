#!/usr/bin/env python3
"""
Migration v12: Add missing columns to all tables

Adds any columns that are referenced in the code but missing from the database.
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
    """Add missing columns to tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Running migration v12: Adding missing columns...")
    
    try:
        changes_made = False
        
        # Add show_leaderboard to contests table
        if not column_exists(cursor, 'contests', 'show_leaderboard'):
            cursor.execute('ALTER TABLE contests ADD COLUMN show_leaderboard BOOLEAN DEFAULT 1')
            print("✓ Added show_leaderboard column to contests table")
            changes_made = True
        else:
            print("✓ show_leaderboard column already exists in contests table")
        
        # Add created_at to users table if missing
        if not column_exists(cursor, 'users', 'created_at'):
            cursor.execute('ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            print("✓ Added created_at column to users table")
            changes_made = True
        else:
            print("✓ created_at column already exists in users table")
        
        # Add reference_solution to problems table if missing
        if not column_exists(cursor, 'problems', 'reference_solution'):
            cursor.execute('ALTER TABLE problems ADD COLUMN reference_solution TEXT')
            print("✓ Added reference_solution column to problems table")
            changes_made = True
        else:
            print("✓ reference_solution column already exists in problems table")
        
        conn.commit()
        
        if changes_made:
            print("\n✓ Migration v12 completed successfully!")
        else:
            print("\n✓ No changes needed - all columns already exist")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
