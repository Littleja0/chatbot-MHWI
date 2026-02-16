import sqlite3

def aggregate_rarity_rates():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    # Feystone tiers
    tiers = [
        'mysterious_feystone_percent', 'glowing_feystone_percent', 
        'worn_feystone_percent', 'warped_feystone_percent',
        'ancient_feystone_percent', 'carved_feystone_percent', 
        'sealed_feystone_percent'
    ]
    
    # Rarity groups (5 to 12)
    rarities = range(5, 13)
    
    print("Aggregate Drop Rates by Rarity (%)")
    header = "Rarity | " + " | ".join([t.replace('_feystone_percent', '')[:3] for t in tiers])
    print(header)
    print("-" * len(header))
    
    for r in rarities:
        row_str = f"  {r:2}   | "
        for t in tiers:
            cursor = conn.execute(f"SELECT SUM({t}) FROM decoration WHERE rarity = ?", (r,))
            rate = cursor.fetchone()[0] or 0.0
            row_str += f"{rate:5.1f} | "
        print(row_str)
    
    conn.close()

if __name__ == "__main__":
    aggregate_rarity_rates()
