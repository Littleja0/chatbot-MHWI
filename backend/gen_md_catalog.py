import sqlite3

def generate_jewel_md():
    conn = sqlite3.connect("d:/chatbot MHWI/backend/mhw.db")
    conn.row_factory = sqlite3.Row
    
    query = """
        SELECT t.name, d.rarity, 
               d.mysterious_feystone_percent as p1, d.glowing_feystone_percent as p2, 
               d.worn_feystone_percent as p3, d.warped_feystone_percent as p4,
               d.ancient_feystone_percent as p5, d.carved_feystone_percent as p6, 
               d.sealed_feystone_percent as p7
        FROM decoration d
        JOIN decoration_text t ON d.id = t.id
        WHERE t.lang_id = 'pt'
        ORDER BY d.rarity DESC, t.name ASC
    """
    
    cursor = conn.execute(query)
    jewels = cursor.fetchall()
    conn.close()
    
    md_content = "# Catálogo Completo de Joias (Adornos) - Monster Hunter World: Iceborne\n\n"
    md_content += "Este arquivo contém a lista completa de joias e suas respectivas taxas de drop por Pedra de Feitiço.\n\n"
    md_content += "| Joia | Raridade | Misteriosa | Cintilante | Gasta | Entalhada | Antiga | Gravada | Selada |\n"
    md_content += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
    
    for j in jewels:
        md_content += f"| {j['name']} | R{j['rarity']} | {j['p1']}% | {j['p2']}% | {j['p3']}% | {j['p4']}% | {j['p5']}% | {j['p6']}% | {j['p7']}% |\n"
    
    # Save to frontend directory
    # Based on main.py, it could be /frontend or /frontend/dist
    # I'll try to put it in both if they exist, or just /frontend
    paths = [
        "d:/chatbot MHWI/frontend/catalogo_completo.md",
        "d:/chatbot MHWI/frontend/dist/catalogo_completo.md"
    ]
    
    success = False
    for p in paths:
        try:
            # Check if directory exists
            if os.path.isdir(os.path.dirname(p)):
                with open(p, "w", encoding="utf-8") as f:
                    f.write(md_content)
                print(f"Catálogo salvo em: {p}")
                success = True
        except Exception as e:
            print(f"Erro ao salvar em {p}: {e}")
            
    if not success:
        # Fallback to backend dir just in case
        with open("d:/chatbot MHWI/backend/catalogo_completo.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        print("Fallback: Catálogo salvo no diretório backend.")

import os
if __name__ == "__main__":
    generate_jewel_md()
