import sqlite3
import os

def sanitize_armor_slots(db_path):
    """
    Detects and fixes armor pieces where slots were incorrectly filled with resistance values.
    Common bug: slot_1=ice, slot_2=dragon.
    """
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    print(f"--- Sanitizando Banco de Dados: {db_path} ---")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Updated heuristic: 
    # Only clean if slot_1 > 1 (tier 2, 3 or 4) AND matches Ice res
    # OR if it's the specific Beotodus IDs which we KNOW are bugged.
    c.execute("""
        SELECT a.id, at.name, a.slot_1, a.slot_2, a.ice, a.dragon
        FROM armor a
        JOIN armor_text at ON a.id = at.id
        WHERE ((a.slot_1 = a.ice AND a.slot_2 = a.dragon AND a.slot_1 > 1) 
               OR (a.id IN (927, 928, 929, 930, 931)))
          AND at.lang_id = 'en'
    """)
    
    suspicious = c.fetchall()
    if not suspicious:
        print("Nenhuma inconsistência de padrão 'Resistência em Slots' detectada.")
        conn.close()
        return

    print(f"Detectadas {len(suspicious)} peças com slots suspeitos (provável erro de importação).")
    
    fixed_count = 0
    for row in suspicious:
        # Heuristic: If it's Alpha+ or standard set, usually has fewer slots or fixed tier.
        # This is tricky because some pieces MIGHT legit have [3, 2].
        # However, the Ice/Dragon match is extremely specific.
        
        # Safe fix: Reset slots to 0 OR try to find the correct value if we can.
        # Since we want to be SAFE and not hallucinate, it's better to show NO slots 
        # than WRONG slots if they match resistances exactly.
        
        # Specific known fixed: Beotodus Alpha+ (927-931)
        if row['id'] in [927, 928, 929, 930, 931]:
            # These we KNOW the fix for
            correct_slots = {
                927: (2, 0), # Head
                928: (3, 0), # Chest
                929: (3, 0), # Arms
                930: (2, 0), # Waist
                931: (2, 0)  # Legs
            }
            s1, s2 = correct_slots[row['id']]
            c.execute("UPDATE armor SET slot_1 = ?, slot_2 = ? WHERE id = ?", (s1, s2, row['id']))
            fixed_count += 1
        else:
            # For others, if the match is exact, we clear them to avoid misinformation
            print(f"Limpando slots suspeitos para ID {row['id']} ({row['name']}) - Slots coincidem com resistências.")
            c.execute("UPDATE armor SET slot_1 = 0, slot_2 = 0 WHERE id = ?", (row['id'],))
            fixed_count += 1

    conn.commit()
    conn.close()
    print(f"✅ Sanitização concluída. {fixed_count} registros corrigidos.")

if __name__ == "__main__":
    db = 'backend/mhw.db'
    sanitize_armor_slots(db)
