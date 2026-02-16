import xml.etree.ElementTree as ET

def revert_xml():
    filename = "d:/chatbot MHWI/rag/armor.xml"
    tree = ET.parse(filename)
    root = tree.getroot()
    
    updated_count = 0
    for record in root.findall("DATA_RECORD"):
        aid = record.find("id").text
        if aid == "1.130":
            slot_elem = record.find("slot_1")
            if slot_elem is not None:
                slot_elem.text = "2"
                print(f"Reverted XML ID 1.130: slot_1 -> 2")
                updated_count += 1
                
    if updated_count > 0:
        tree.write(filename, encoding="UTF-8", xml_declaration=True)
        print("XML updated successfully.")
    else:
        print("No records found to update.")

if __name__ == "__main__":
    revert_xml()
