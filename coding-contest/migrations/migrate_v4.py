#!/usr/bin/env python3
"""
Migration script to add settings table and leaderboard toggle.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME


def migrate_v4():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Starting migration v4...")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('leaderboard_enabled', '1')")

    conn.commit()
    conn.close()
    print("\n✓ Migration v4 completed")


if __name__ == '__main__':
    migrate_v4()
