#!/usr/bin/env python3
"""
Migration v11: Create admin_logs table

Adds admin action logging for audit trail.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

def migrate():
    """Add admin_logs table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Running migration v11: Creating admin_logs table...")
    
    try:
        # Create admin_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id 
            ON admin_logs(admin_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at 
            ON admin_logs(created_at DESC)
        ''')
        
        conn.commit()
        print("✓ admin_logs table created successfully")
        print("✓ Indexes created")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\n✓ Migration v11 completed successfully!")

if __name__ == '__main__':
    migrate()
