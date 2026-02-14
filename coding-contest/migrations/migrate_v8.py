#!/usr/bin/env python3
"""
Migration v8: Add constraints field to problems table
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'contest.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Migration v8: Adding constraints field to problems table")
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(problems)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'constraints' not in columns:
            # Add constraints column
            cursor.execute('''
                ALTER TABLE problems 
                ADD COLUMN constraints TEXT DEFAULT ''
            ''')
            print("✓ Added 'constraints' column to problems table")
        else:
            print("✓ 'constraints' column already exists")
        
        conn.commit()
        print("✓ Migration v8 completed successfully")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
