import os
import sys
from pathlib import Path

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

TOOLS_DIR = Path("game_extractor/tools")
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

def check_tools():
    print("="*60)
    print("VERIFICANDO FERRAMENTAS DE EXTRAÇÃO")
    print("="*60)
    
    tools = ["WorldChunkTool.exe", "MHWNoChunk.exe"]
    found = []
    
    for tool in tools:
        if (TOOLS_DIR / tool).exists():
            found.append(tool)
    
    if found:
        print(f"[OK] Ferramentas encontradas: {', '.join(found)}")
        return True
    else:
        print("[X] NENHUMA FERRAMENTA ENCONTRADA")
        print(f"Diretório: {TOOLS_DIR.absolute()}")
        print("\nPara extrair dados da Cantina, Safari, etc., precisamos do WorldChunkTool.")
        print("Por favor, baixe 'WorldChunkTool.exe' e coloque na pasta acima.")
        print("Link: https://github.com/mhvuze/WorldChunkTool/releases")
        return False

if __name__ == "__main__":
    check_tools()
