#!/usr/bin/env python3
"""
Migration script for Phase 2 Refactoring (Multi-Contest Support).
Migrates data from legacy schema to HackerRank-style architecture.
"""

import sqlite3
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

def migrate_v2():
    print("Starting Phase 2 Database Migration...")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Create 'contests' table (new plural name)
    print("Creating 'contests' table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Migrate data from legacy 'contest' table if it exists
    try:
        legacy_contest = cursor.execute("SELECT * FROM contest ORDER BY id DESC LIMIT 1").fetchone()
        if legacy_contest:
            # Convert Row to dict to use .get() safe access
            contest_data = dict(legacy_contest)
            print(f"Found legacy contest: {contest_data['name']}")
            
            cursor.execute('''
                INSERT INTO contests (title, start_time, end_time, is_active, created_at, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                contest_data['name'], 
                contest_data['start_time'], 
                contest_data['end_time'], 
                contest_data['is_active'], 
                contest_data['created_at'],
                contest_data.get('description', '') 
            ))
            new_contest_id = cursor.lastrowid
            print(f"Migrated legacy contest to new 'contests' table with ID: {new_contest_id}")
            
            # Optional: Drop legacy table? Let's keep it for safety for now, or just ignore it.
            # cursor.execute("DROP TABLE contest") 
        else:
            print("No legacy contest data found.")
            new_contest_id = None
            
    except sqlite3.OperationalError:
        print("Legacy 'contest' table not found. Skipping data migration.")
        new_contest_id = None

    # 3. Add 'contest_id' to 'problems'
    print("Updating 'problems' table...")
    try:
        cursor.execute("ALTER TABLE problems ADD COLUMN contest_id INTEGER REFERENCES contests(id)")
        print("Added 'contest_id' column to problems.")
        
        # If we migrated a contest, should we assign all existing problems to it?
        # Let's assign them to the migrated contest so they don't disappear from the default view
        if new_contest_id:
             cursor.execute("UPDATE problems SET contest_id = ?", (new_contest_id,))
             print(f"Assigned all existing problems to contest ID {new_contest_id}")
             
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("'contest_id' column already exists in problems.")
        else:
             print(f"Error altering problems table: {e}")

    # 4. Add 'contest_id' to 'submissions'
    print("Updating 'submissions' table...")
    try:
        cursor.execute("ALTER TABLE submissions ADD COLUMN contest_id INTEGER REFERENCES contests(id)")
        print("Added 'contest_id' column to submissions.")
        
        # Backfill submission contest_ids based on their problems
        print("Backfilling submission contest mappings...")
        cursor.execute('''
            UPDATE submissions 
            SET contest_id = (SELECT contest_id FROM problems WHERE problems.id = submissions.problem_id)
        ''')
        print("Backfill complete.")
        
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("'contest_id' column already exists in submissions.")
        else:
            print(f"Error altering submissions table: {e}")

    conn.commit()
    conn.close()
    print("\n✓ Migration V2 completed successfully!")

if __name__ == '__main__':
    migrate_v2()
