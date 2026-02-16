import sqlite3
import xml.etree.ElementTree as ET

def generate_jewel_catalog():
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
    
    # Split into multiple records to avoid huge single documents
    chunk_size = 40
    root = ET.Element("jewel_catalog")
    
    for i in range(0, len(jewels), chunk_size):
        chunk = jewels[i:i + chunk_size]
        record = ET.SubElement(root, "DATA_RECORD")
        topic = ET.SubElement(record, "topic")
        topic.text = f"Catálogo de Joias e Drop Rates - Parte {i//chunk_size + 1}"
        
        content = ET.SubElement(record, "content")
        lines = ["| Joia | Raridade | Drop Rates (%) |", "| :--- | :---: | :--- |"]
        
        for j in chunk:
            rates = []
            if j['p1'] > 0: rates.append(f"Misteriosa: {j['p1']}%")
            if j['p2'] > 0: rates.append(f"Cintilante: {j['p2']}%")
            if j['p3'] > 0: rates.append(f"Gasta: {j['p3']}%")
            if j['p4'] > 0: rates.append(f"Entalhada: {j['p4']}%")
            if j['p5'] > 0: rates.append(f"Antiga: {j['p5']}%")
            if j['p6'] > 0: rates.append(f"Gravada: {j['p6']}%")
            if j['p7'] > 0: rates.append(f"Selada: {j['p7']}%")
            
            rate_str = "<br>".join(rates)
            lines.append(f"| {j['name']} | R{j['rarity']} | {rate_str} |")
        
        content.text = "\n".join(lines)
        
    tree = ET.ElementTree(root)
    tree.write("d:/chatbot MHWI/rag/jewel_catalog.xml", encoding="UTF-8", xml_declaration=True)
    print(f"Geradas {len(jewels)} joias em jewel_catalog.xml")

if __name__ == "__main__":
    generate_jewel_catalog()
