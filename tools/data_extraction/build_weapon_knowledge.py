import sqlite3
import os
import json

def export_weapon_knowledge():
    db_path = "backend/mhw.db"
    base_dir = "knowledge/weapons"
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Mapeamento de tipos internos para nomes amigáveis (ajustado para bater com o jogo)
    type_map = {
        "great-sword": 0, "sword-and-shield": 1, "dual-blades": 2, "long-sword": 3,
        "hammer": 4, "hunting-horn": 5, "lance": 6, "gunlance": 7, "switch-axe": 8,
        "charge-blade": 9, "insect-glaive": 10, "bow": 11, "heavy-bowgun": 12, "light-bowgun": 13
    }
    
    friendly_names = {
        0: "Grande Espada", 1: "Espada e Escudo", 2: "Espada Dupla", 3: "Espada Longa",
        4: "Martelo", 5: "Lança de Caça", 6: "Lança", 7: "Lança-Canhão", 8: "Espada-Machado",
        9: "Espadão de Carga", 10: "Glaive de Inseto", 11: "Arco", 12: "Metralhadora Pesada", 13: "Metralhadora Leve"
    }

    print("Gerando enciclopédia de armas...")

    # Pegar todas as armas e seus textos
    query = """
    SELECT w.id, w.weapon_type, w.rarity, w.attack, wt.name, w.element1, w.element1_attack
    FROM weapon w
    JOIN weapon_text wt ON w.id = wt.id
    WHERE wt.lang_id = 'pt'
    ORDER BY w.weapon_type, w.rarity, w.id
    """
    
    cur.execute(query)
    weapons = cur.fetchall()

    # Organizar por tipo
    by_type = {}
    for w in weapons:
        wid, wtype, rarity, attack, name, elem, elem_atk = w
        tid = type_map.get(wtype, -1)
        if tid not in by_type: by_type[tid] = []
        by_type[tid].append({
            "id": wid,
            "name": name,
            "rarity": rarity,
            "attack": attack,
            "element": f"{elem} ({elem_atk})" if elem else "Nenhum"
        })

    # Criar arquivos por categoria
    for tid, items in by_type.items():
        if tid == -1: continue
        
        folder_name = f"{tid}_{friendly_names[tid].replace(' ', '_')}"
        file_path = f"{base_dir}/{folder_name}.md"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Categoria {tid}: {friendly_names[tid]}\n\n")
            f.write("Esta é a árvore de forja oficial mapeada pelo Gojo. Use estes IDs como verdade absoluta.\n\n")
            
            # Agrupar por raridade para simular progressão da árvore
            items_by_rarity = {}
            for item in items:
                r = item["rarity"]
                if r not in items_by_rarity: items_by_rarity[r] = []
                items_by_rarity[r].append(item)
                
            for r in sorted(items_by_rarity.keys()):
                f.write(f"## Raridade {r}\n")
                for item in items_by_rarity[r]:
                    f.write(f"- **{item['name']}** (ID: {item['id']}) | Ataque: {item['attack']} | Elemento: {item['element']}\n")
                f.write("\n")

    conn.close()
    print("Enciclopédia gerada com sucesso em /knowledge/weapons/")

if __name__ == "__main__":
    export_weapon_knowledge()
