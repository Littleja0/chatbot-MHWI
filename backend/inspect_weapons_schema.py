
import sqlite3
import os

DB_PATH = 'mhw.db'

def inspect():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n--- Full Table Info: weapon ---")
    cursor.execute("PRAGMA table_info(weapon)")
    for row in cursor.fetchall():
        print(f"{row['name']} ({row['type']})")

    # Check distinct weapon types
    print("\n--- Weapon Types ---")
    cursor.execute("SELECT DISTINCT weapon_type FROM weapon LIMIT 5")
    for row in cursor.fetchall():
        print(row[0])


    conn.close()

if __name__ == "__main__":
    inspect()
