#!/usr/bin/env python3
"""
Migration script to add function-style and difficulty fields.
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
import config

DB_NAME = config.DB_NAME

COLUMNS = [
    ("problem_type", "TEXT", "'coding'"),
    ("starter_code", "TEXT", None),
    ("round_number", "INTEGER", "1"),
    ("problem_mode", "TEXT", "'stdin'"),
    ("function_name", "TEXT", "'solve'"),
    ("difficulty", "TEXT", "'easy'"),
]


def migrate_v3():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Starting migration v3...")

    # Get existing columns
    cursor.execute("PRAGMA table_info(problems)")
    existing = {row[1] for row in cursor.fetchall()}

    for name, col_type, default in COLUMNS:
        if name in existing:
            print(f"✓ Column '{name}' already exists")
            continue
        default_sql = f" DEFAULT {default}" if default is not None else ""
        cursor.execute(f"ALTER TABLE problems ADD COLUMN {name} {col_type}{default_sql}")
        print(f"✓ Added column '{name}'")

    conn.commit()
    conn.close()
    print("\n✓ Migration v3 completed")


if __name__ == '__main__':
    migrate_v3()
