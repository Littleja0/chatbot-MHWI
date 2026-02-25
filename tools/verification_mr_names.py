import sqlite3

def verify_mr_data():
    conn = sqlite3.connect("data/mhw.db")
    cursor = conn.cursor()
    
    print("--- Rank Breakdown ---")
    ranks = cursor.execute("SELECT rank, count(*) FROM wiki_weapon GROUP BY rank").fetchall()
    for r in ranks:
        print(f"Rank {r[0]}: {r[1]}")
        
    print("\n--- Specific Check: Chrome Deathscythe I ---")
    rows = cursor.execute("SELECT name, rank, rarity, attack, affinity, element FROM wiki_weapon WHERE name LIKE '%Chrome Deathscythe I%'").fetchall()
    for row in rows:
        print(row)
        
    print("\n--- Specific Check: Purgation's Atrocity ---")
    rows = cursor.execute("SELECT name, rank, rarity, attack, affinity, element FROM wiki_weapon WHERE name LIKE '%Purgation%Atrocity%'").fetchall()
    for row in rows:
        print(row)

    print("\n--- Random MR Sample ---")
    rows = cursor.execute("SELECT name, rarity FROM wiki_weapon WHERE rank='MR' ORDER BY RANDOM() LIMIT 5").fetchall()
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    verify_mr_data()
