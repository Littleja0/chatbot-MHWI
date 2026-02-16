import sqlite3

def check_schemas():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    for table in ['tool', 'quest', 'decoration']:
        print(f"--- Schema for {table} ---")
        cursor = conn.execute(f"PRAGMA table_info({table})")
        for col in cursor.fetchall():
            print(col)
    conn.close()

if __name__ == "__main__":
    check_schemas()
