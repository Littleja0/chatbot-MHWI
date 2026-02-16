import sqlite3

def get_deco_rates():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    # Select a few representative decorations (Attack Jewel, Expert, etc.)
    # Attack Jewel 1 (ID 17?), Attack Jewel 4 (ID 6xx?)
    cursor = conn.execute("""
        SELECT d.id, t.name, d.rarity, 
               d.mysterious_feystone_percent, d.glowing_feystone_percent, 
               d.worn_feystone_percent, d.warped_feystone_percent,
               d.ancient_feystone_percent, d.carved_feystone_percent, 
               d.sealed_feystone_percent
        FROM decoration d
        JOIN decoration_text t ON d.id = t.id
        WHERE t.lang_id = 'pt' AND (t.name LIKE '%Ataque%' OR t.name LIKE '%Especialista%' OR t.name LIKE '%Crítico%')
        LIMIT 20
    """)
    for row in cursor:
        print(f"Name: {row['name']} (R{row['rarity']})")
        print(f"  Mys: {row['mysterious_feystone_percent']}% | Glo: {row['glowing_feystone_percent']}% | Wor: {row['worn_feystone_percent']}% | War: {row['warped_feystone_percent']}%")
        print(f"  Anc: {row['ancient_feystone_percent']}% | Car: {row['carved_feystone_percent']}% | Sea: {row['sealed_feystone_percent']}%")
    conn.close()

if __name__ == "__main__":
    get_deco_rates()
