
import xml.etree.ElementTree as ET
from pathlib import Path

def find_bone_ids():
    armor_text_path = Path("rag/armor_text.xml")
    tree = ET.parse(armor_text_path)
    root = tree.getroot()
    ids = []
    for record in root.findall("DATA_RECORD"):
        name = record.find("name")
        if name is not None and name.text and "Elmo Ósseo α+" in name.text:
            ids.append(record.find("id").text)
    
    print(f"IDs with 'Elmo Ósseo α+': {ids}")
    
    armor_path = Path("rag/armor.xml")
    tree = ET.parse(armor_path)
    root = tree.getroot()
    for record in root.findall("DATA_RECORD"):
        aid = record.find("id").text
        if aid in ids:
            print(f"Armor ID {aid} -> Armorset ID: {record.find('armorset_id').text}")

if __name__ == "__main__":
    find_bone_ids()
