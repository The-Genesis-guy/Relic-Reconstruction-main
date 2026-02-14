#!/usr/bin/env python3
"""
Migration script to add admin_logs table for tracking admin actions.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME


def migrate_v6():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Starting migration v6...")

    # Check if admin_logs table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='admin_logs'
    """)
    
    if cursor.fetchone():
        print("✓ admin_logs table already exists")
    else:
        cursor.execute("""
            CREATE TABLE admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id)
            )
        """)
        print("✓ Created admin_logs table")
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX idx_admin_logs_admin_id ON admin_logs(admin_id)
        """)
        cursor.execute("""
            CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at)
        """)
        print("✓ Created indexes on admin_logs")

    conn.commit()
    conn.close()
    print("\n✓ Migration v6 completed")


if __name__ == '__main__':
    migrate_v6()
