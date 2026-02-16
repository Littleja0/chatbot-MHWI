import sqlite3

def list_tables():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    conn.close()

if __name__ == "__main__":
    list_tables()
