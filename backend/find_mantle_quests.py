import xml.etree.ElementTree as ET

def find_mantle_unlock_quests():
    filename = "d:/chatbot MHWI/rag/quest_text.xml"
    tree = ET.parse(filename)
    root = tree.getroot()
    keywords = ["desbloqueia", "libera", "ganha", "obter", "unlock", "reward", "manto", "mantle"]
    for record in root.findall("DATA_RECORD"):
        lang = record.find("lang_id").text
        if lang in ['pt', 'en']:
            name = record.find("name").text or ""
            desc = record.find("description").text or ""
            if "manto" in desc.lower() or "mantle" in desc.lower():
                print(f"[{lang}] Quest: {name}")
                print(f"Desc: {desc}\n")

if __name__ == "__main__":
    find_mantle_unlock_quests()
