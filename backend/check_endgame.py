
import sqlite3

def check_endgame_monsters():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    try:
        print("--- CHECKING FOR ENDGAME MONSTERS ---")
        
        monsters_to_check = ["Alatreon", "Fatalis", "Safi'jiiva", "Raging Brachydios", "Furious Rajang"]
        
        for monster in monsters_to_check:
            cursor = conn.execute("SELECT count(*) FROM monster_text WHERE name LIKE ? AND lang_id='en'", (f"%{monster}%",))
            count = cursor.fetchone()[0]
            print(f"{monster}: {'Present' if count > 0 else 'MISSING'}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_endgame_monsters()
