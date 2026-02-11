
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

    # 1. Check table info
    print("\n--- Table Info: weapon ---")
    cursor.execute("PRAGMA table_info(weapon)")
    for row in cursor.fetchall():
        print(dict(row))

    # 2. Check for existence of lower tier weapons
    print("\n--- Checking for lower tier weapons (e.g., %Iron%) ---")
    query = """
        SELECT w.id, wt.name, w.rarity 
        FROM weapon w 
        JOIN weapon_text wt ON w.id = wt.id 
        WHERE wt.lang_id = 'en' AND wt.name LIKE '%Iron%' 
        LIMIT 10
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            print("No weapons found with 'Iron' in name. Trying another common low rank name.")
            cursor.execute("SELECT w.id, wt.name, w.rarity FROM weapon w JOIN weapon_text wt ON w.id = wt.id WHERE wt.lang_id = 'en' LIMIT 10")
            rows = cursor.fetchall()
        
        for row in rows:
            print(dict(row))
    except Exception as e:
        print(f"Error querying weapons: {e}")

    # 3. Check total count
    cursor.execute("SELECT COUNT(*) FROM weapon")
    count = cursor.fetchone()[0]
    print(f"\nTotal weapons in DB: {count}")

    conn.close()

if __name__ == "__main__":
    inspect()
