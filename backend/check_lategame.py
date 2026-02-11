
import sqlite3

def check_late_game_armor():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- CHECKING ESCADORA (ALATREON) ARMOR ---")
        cursor = conn.execute("SELECT name FROM armor_text WHERE name LIKE '%Escadora%' AND lang_id='en'")
        found = cursor.fetchall()
        if found:
            print(f"Found {len(found)} Escadora pieces.")
        else:
            print("Escadora (Alatreon) armor NOT found.")

        print("\n--- CHECKING HIGH RARITY ARMOR (>11) ---")
        cursor = conn.execute("""
            SELECT count(*), max(rarity) 
            FROM armor 
            WHERE rarity >= 12
        """)
        stats = cursor.fetchone()
        print(f"Number of Rarity 12+ pieces: {stats[0]}")
        print(f"Max Rarity found: {stats[1]}")
        
        print("\n--- LISTING SOME RARITY 12 ARMOR NAMES ---")
        cursor = conn.execute("""
            SELECT DISTINCT at.name 
            FROM armor a 
            JOIN armor_text at ON a.id = at.id
            WHERE a.rarity >= 12 AND at.lang_id = 'en'
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"- {row['name']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_late_game_armor()
