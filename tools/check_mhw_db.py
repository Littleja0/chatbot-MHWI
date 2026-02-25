import sqlite3
import pandas as pd

def check_db():
    conn = sqlite3.connect("data/mhw.db")
    
    print("--- Armor Table Counts ---")
    counts = pd.read_sql("SELECT rank, count(*) as count FROM armor GROUP BY rank", conn)
    print(counts)
    
    print("\n--- Sample Armor Data ---")
    sample = pd.read_sql("""
        SELECT a.id, at.name, a.rank, a.rarity, a.slot_1, a.slot_2, a.slot_3
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        WHERE at.lang_id = 'pt'
        LIMIT 5
    """, conn)
    print(sample)
    
    conn.close()

if __name__ == "__main__":
    check_db()
