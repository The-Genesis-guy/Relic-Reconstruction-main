#!/usr/bin/env python3
"""
Migration v13: Add show_scores_to_students setting

Adds a global setting to control whether students can see their scores.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

def migrate():
    """Add show_scores_to_students setting."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Running migration v13: Adding show_scores_to_students setting...")
    
    try:
        # Add the setting (default: enabled)
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('show_scores_to_students', '1')
        ''')
        
        conn.commit()
        print("✓ show_scores_to_students setting added (default: enabled)")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\n✓ Migration v13 completed successfully!")

if __name__ == '__main__':
    migrate()
