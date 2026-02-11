
import sqlite3

def check_db():
    try:
        conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found ({len(tables)}): {tables[:5]}...")
        
        if 'armor' in tables:
            cursor.execute("SELECT count(*) FROM armor")
            print(f"Armor pieces: {cursor.fetchone()[0]}")
            
            cursor.execute("SELECT DISTINCT rank FROM armor")
            print(f"Ranks present: {[r[0] for r in cursor.fetchall()]}")
            
        if 'monster_text' in tables:
            cursor.execute("SELECT count(*) FROM monster_text WHERE name = 'Velkhana'")
            print(f"Velkhana entries: {cursor.fetchone()[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_db()
