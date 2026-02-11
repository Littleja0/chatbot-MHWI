import os
import xml.etree.ElementTree as ET
from pathlib import Path

# Configurações
RAG_PATH = Path("rag")
LANGS_TO_KEEP = ["pt", "en"]

def slim_xml_files():
    """
    Percorre todos os arquivos XML na pasta 'rag/' e remove registros que não sejam 
    os idiomas desejados (PT e EN). Isso reduz o tamanho dos arquivos e economiza tokens.
    """
    if not RAG_PATH.exists():
        print(f"Erro: Pasta {RAG_PATH} não encontrada.")
        return

    print(f"🚀 Iniciando limpeza de XMLs na pasta '{RAG_PATH}'...")
    total_removed = 0
    total_saved_kb = 0

    for xml_file in RAG_PATH.glob("*.xml"):
        original_size = xml_file.stat().st_size
        print(f"📄 Processando: {xml_file.name} ({original_size / 1024:.1f} KB)")

        try:
            # Usar ET para parsear
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Encontrar todos os DATA_RECORD
            records = root.findall("DATA_RECORD")
            removed_in_file = 0
            
            for record in records:
                lang_node = record.find("lang_id")
                # Se o arquivo não tem lang_id (ex: monster.xml que é só dados), mantemos tudo
                if lang_node is not None:
                    if lang_node.text not in LANGS_TO_KEEP:
                        root.remove(record)
                        removed_in_file += 1
            
            if removed_in_file > 0:
                # Salvar o arquivo limpo
                tree.write(xml_file, encoding="UTF-8", xml_declaration=True)
                new_size = xml_file.stat().st_size
                saved = (original_size - new_size) / 1024
                print(f"  ✅ Removidos {removed_in_file} registros. Economia: {saved:.1f} KB")
                total_removed += removed_in_file
                total_saved_kb += saved
            else:
                print("  ℹ️ Nenhuma alteração necessária.")

        except Exception as e:
            print(f"  ❌ Erro ao processar {xml_file.name}: {e}")

    print("\n" + "="*30)
    print(f"✨ LIMPEZA CONCLUÍDA ✨")
    print(f"Registros removidos: {total_removed}")
    print(f"Espaço total economizado: {total_saved_kb / 1024:.2f} MB")
    print("="*30)

if __name__ == "__main__":
    slim_xml_files()
