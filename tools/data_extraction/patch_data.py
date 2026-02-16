
import xml.etree.ElementTree as ET
import sqlite3
import os

RAG_PATH = "rag"

def patch_xml(filename, record_tag, match_field, match_value, update_dict):
    path = os.path.join(RAG_PATH, filename)
    tree = ET.parse(path)
    root = tree.getroot()
    count = 0
    for rec in root.findall("DATA_RECORD"):
        field = rec.find(match_field)
        if field is not None and field.text == match_value:
            for k, v in update_dict.items():
                target = rec.find(k)
                if target is not None:
                    target.text = str(v)
                else:
                    new_tag = ET.SubElement(rec, k)
                    new_tag.text = str(v)
            count += 1
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print(f"Patched {count} records in {filename}")

def add_xml_record(filename, data_dict):
    path = os.path.join(RAG_PATH, filename)
    tree = ET.parse(path)
    root = tree.getroot()
    rec = ET.SubElement(root, "DATA_RECORD")
    for k, v in data_dict.items():
        child = ET.SubElement(rec, k)
        child.text = str(v)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print(f"Added record to {filename}")

def delete_xml_records(filename, match_field, match_value):
    path = os.path.join(RAG_PATH, filename)
    tree = ET.parse(path)
    root = tree.getroot()
    to_remove = []
    for rec in root.findall("DATA_RECORD"):
        field = rec.find(match_field)
        if field is not None and field.text == match_value:
            to_remove.append(rec)
    for rec in to_remove:
        root.remove(rec)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    print(f"Deleted {len(to_remove)} records from {filename}")

# --- LAVASIOTH ALPHA+ FIXES ---
# Helm 1.167: Fire Attack Level 1
patch_xml("armor_skill.xml", "DATA_RECORD", "armor_id", "1.167", {"level": 1}) # Search matches any skill of this armor, need finer grain
# More precise patch for Helm skill 26
def patch_armor_skill(armor_id, skill_id, new_level):
    path = os.path.join(RAG_PATH, "armor_skill.xml")
    tree = ET.parse(path)
    root = tree.getroot()
    for rec in root.findall("DATA_RECORD"):
        aid = rec.find("armor_id")
        sid = rec.find("skilltree_id")
        if aid is not None and aid.text == armor_id and sid is not None and sid.text == str(skill_id):
            rec.find("level").text = str(new_level)
    tree.write(path, encoding="UTF-8", xml_declaration=True)

patch_armor_skill("1.167", 26, 1) # Helm Fire Attack 2 -> 1
patch_xml("armor.xml", "DATA_RECORD", "id", "1.168", {"slot_1": 2, "slot_2": 1}) # Mail slots 1,1 -> 2,1

# --- ODOGARON ALPHA+ SLOT FIXES ---
patch_xml("armor.xml", "DATA_RECORD", "id", "1.147", {"slot_1": 3}) # Helm 2 -> 3
patch_xml("armor.xml", "DATA_RECORD", "id", "1.149", {"slot_1": 2}) # Arms 1 -> 2

# --- ODOGARON BONUS FIXES ---
delete_xml_records("armorset_bonus_skill.xml", "setbonus_id", "35")
add_xml_record("armorset_bonus_skill.xml", {"setbonus_id": 35, "skilltree_id": 128, "required": 2}) # Punishing Draw
add_xml_record("armorset_bonus_skill.xml", {"setbonus_id": 35, "skilltree_id": 129, "required": 4}) # Protective Polish

# --- DB SYNC ---
conn = sqlite3.connect("backend/mhw.db")
cur = conn.cursor()
# Lavasioth Helm Skill
cur.execute("UPDATE armor_skill SET level = 1 WHERE armor_id = 1167 AND skilltree_id = 26")
# Lavasioth Mail Slots
cur.execute("UPDATE armor SET slot_1 = 2, slot_2 = 1 WHERE id = 1168")
# Odogaron Alpha+ Slots
cur.execute("UPDATE armor SET slot_1 = 3 WHERE id = 1147")
cur.execute("UPDATE armor SET slot_1 = 2 WHERE id = 1149")
# Odogaron Bonus
cur.execute("DELETE FROM armorset_bonus_skill WHERE setbonus_id = 35")
cur.execute("INSERT INTO armorset_bonus_skill (setbonus_id, skilltree_id, required) VALUES (35, 128, 2)")
cur.execute("INSERT INTO armorset_bonus_skill (setbonus_id, skilltree_id, required) VALUES (35, 129, 4)")
conn.commit()
conn.close()
print("DB Sync Complete")
