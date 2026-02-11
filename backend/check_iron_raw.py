
import sqlite3
import os

DB_PATH = 'mhw.db'

def check_iron():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT wt.name, w.attack_true FROM weapon w JOIN weapon_text wt ON w.id = wt.id WHERE wt.name = 'Iron Katana I' LIMIT 1")
        print(dict(cursor.fetchone()))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_iron()
