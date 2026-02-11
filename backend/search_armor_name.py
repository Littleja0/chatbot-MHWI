
import sqlite3

def search_armor_names():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- Searching for Velkhana/Rimeguard Armor ---")
        cursor = conn.execute("SELECT name, lang_id FROM armor_text WHERE (name LIKE '%Velkhana%' OR name LIKE '%Rime%') AND lang_id='en'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Found: {row['name']} ({row['lang_id']})")
            
        print("\n--- Searching for Velkhana/Rimeguard Armor (PT) ---")
        cursor = conn.execute("SELECT name, lang_id FROM armor_text WHERE (name LIKE '%Velkhana%' OR name LIKE '%Rime%') AND lang_id='pt'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Found: {row['name']} ({row['lang_id']})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    search_armor_names()
