import sqlite3

conn = sqlite3.connect('mhw.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Buscar Challenger/Desafiante charm
print("=== Charm Desafiante - Dados de Crafting ===\n")

c.execute("""
    SELECT c.id, c.rarity, c.recipe_id, c.previous_id, ct.name
    FROM charm c
    JOIN charm_text ct ON c.id = ct.id
    WHERE ct.name LIKE '%Desafiante%' OR ct.name LIKE '%Challenger%'
    AND ct.lang_id = 'pt'
    ORDER BY c.rarity
""")

charms = c.fetchall()
for charm in charms:
    print(f"\n{charm['name']} (Raridade {charm['rarity']})")
    print(f"  ID: {charm['id']}, Recipe ID: {charm['recipe_id']}, Previous ID: {charm['previous_id']}")
    
    if charm['recipe_id']:
        # Buscar materiais
        c.execute("""
            SELECT it.name, ri.quantity
            FROM recipe_item ri
            JOIN item_text it ON ri.item_id = it.id
            WHERE ri.recipe_id = ? AND it.lang_id = 'pt'
        """, (charm['recipe_id'],))
        materials = c.fetchall()
        if materials:
            print("  Materiais:")
            for m in materials:
                print(f"    - {m['name']} x{m['quantity']}")
        else:
            print("  (Sem materiais listados)")

conn.close()
