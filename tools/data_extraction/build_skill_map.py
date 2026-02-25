import sqlite3
import json
from pathlib import Path

def build_skill_map():
    conn = sqlite3.connect("data/mhw.db")
    
    # Pegar nomes em EN e seus respectivos IDs de skilltree
    # s.id em skilltree_text é o id da skilltree
    query = """
        SELECT st_en.name as name_en, st_pt.name as name_pt, st_en.id
        FROM skilltree_text st_en
        JOIN skilltree_text st_pt ON st_en.id = st_pt.id
        WHERE st_en.lang_id = 'en' AND st_pt.lang_id = 'pt'
    """
    
    mapping = {}
    cursor = conn.cursor()
    for row in cursor.execute(query):
        name_en, name_pt, id = row
        # Sanitizar nomes (remover espaços extras, etc)
        mapping[name_en.strip().lower()] = {
            "name_pt": name_pt.strip(),
            "id": id
        }
    
    conn.close()
    
    output_path = Path("data/skill_mapping.json")
    output_path.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Mapeamento de {len(mapping)} skills salvo em {output_path}")

if __name__ == "__main__":
    build_skill_map()
