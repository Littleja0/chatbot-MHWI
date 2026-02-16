import xml.etree.ElementTree as ET

def find_quest_keywords():
    filename = "d:/chatbot MHWI/rag/quest_text.xml"
    tree = ET.parse(filename)
    root = tree.getroot()
    keywords = ["Temporal", "Evasão", "Rocha-firme", "Evasion", "Rocksteady"]
    for record in root.findall("DATA_RECORD"):
        lang = record.find("lang_id").text
        if lang in ['pt', 'en']:
            name = record.find("name").text or ""
            desc = record.find("description").text or ""
            if any(k in name or k in desc for k in keywords):
                print(f"[{lang}] Quest: {name}")
                print(f"Desc: {desc}\n")

if __name__ == "__main__":
    find_quest_keywords()
