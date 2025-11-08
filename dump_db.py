import sqlite3
import os

DB_PATH = 'finvestacore.db'

# Check if DB exists
if not os.path.exists(DB_PATH):
    print(f"Error: {DB_PATH} not found! Run app.py first to create DB.")
else:
    # Connect and dump
    conn = sqlite3.connect(DB_PATH)
    with open('backup.sql', 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
    conn.close()
    print("✅ Backup created: backup.sql (full DB dump with data)")