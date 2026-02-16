import xml.etree.ElementTree as ET

def check_quests_for_mantles():
    filename = "d:/chatbot MHWI/rag/quest_text.xml"
    tree = ET.parse(filename)
    root = tree.getroot()
    count = 0
    for record in root.findall("DATA_RECORD"):
        lang = record.find("lang_id").text
        if lang == 'pt':
            name = record.find("name").text or ""
            obj = record.find("objective").text or ""
            desc = record.find("description").text or ""
            if "Manto" in name or "Manto" in obj or "Manto" in desc:
                print(f"Quest: {name}")
                print(f"Obj: {obj}")
                print(f"Desc: {desc}\n")
                count += 1
    print(f"Total matches: {count}")

if __name__ == "__main__":
    check_quests_for_mantles()
