import xml.etree.ElementTree as ET

def check_tools_xml():
    filename = "d:/chatbot MHWI/rag/tool_text.xml"
    tree = ET.parse(filename)
    root = tree.getroot()
    for record in root.findall("DATA_RECORD"):
        if record.find("lang_id").text == 'pt':
            name = record.find("name").text
            desc = record.find("description").text
            if "Manto" in name:
                print(f"Name: {name}")
                print(f"Desc: {desc}\n")

if __name__ == "__main__":
    check_tools_xml()
