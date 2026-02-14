#!/usr/bin/env python3
"""
Migration script to add submissions scoring columns.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

COLUMNS = [
    ("points_awarded", "INTEGER", "0"),
    ("tests_passed", "INTEGER", "0"),
    ("tests_total", "INTEGER", "0"),
]


def migrate_v5():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Starting migration v5...")

    cursor.execute("PRAGMA table_info(submissions)")
    existing = {row[1] for row in cursor.fetchall()}

    for name, col_type, default in COLUMNS:
        if name in existing:
            print(f"✓ Column '{name}' already exists")
            continue
        cursor.execute(f"ALTER TABLE submissions ADD COLUMN {name} {col_type} DEFAULT {default}")
        print(f"✓ Added column '{name}'")

    conn.commit()
    conn.close()
    print("\n✓ Migration v5 completed")


if __name__ == '__main__':
    migrate_v5()
