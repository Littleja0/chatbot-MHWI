"""
Script para localizar e listar os arquivos do jogo MHW
"""
import os
from pathlib import Path

# Caminho do jogo
MHW_PATH = Path(r"D:\Steam\steamapps\common\Monster Hunter World")

print("=" * 60)
print("VERIFICANDO ARQUIVOS DO MONSTER HUNTER WORLD")
print("=" * 60)

if not MHW_PATH.exists():
    print(f"❌ Caminho não encontrado: {MHW_PATH}")
    exit(1)

print(f"✅ Jogo encontrado em: {MHW_PATH}")

# Listar chunks
print("\n=== ARQUIVOS CHUNK ===")
chunks = list(MHW_PATH.glob("chunk*.bin")) + list(MHW_PATH.glob("chunkG*.bin"))
chunks.sort()

total_size = 0
for chunk in chunks:
    size_gb = chunk.stat().st_size / (1024**3)
    total_size += size_gb
    print(f"  {chunk.name}: {size_gb:.2f} GB")

print(f"\nTotal: {len(chunks)} chunks, {total_size:.2f} GB")

# Verificar se é Iceborne
iceborne_chunks = [c for c in chunks if 'G' in c.name]
print(f"\n{'✅ Iceborne detectado!' if iceborne_chunks else '⚠️ Versão base (sem Iceborne)'}")

# Verificar pasta nativePC (mods ou arquivos extraídos)
native_pc = MHW_PATH / "nativePC"
if native_pc.exists():
    print(f"\n=== PASTA nativePC ENCONTRADA ===")
    # Listar subpastas
    for item in native_pc.iterdir():
        if item.is_dir():
            count = len(list(item.rglob("*")))
            print(f"  📁 {item.name}/ ({count} arquivos)")

# Verificar ferramentas de extração
print("\n=== VERIFICANDO FERRAMENTAS ===")
tools_dir = Path(__file__).parent / "game_extractor" / "tools"
tools_dir.mkdir(exist_ok=True)

tools = ["WorldChunkTool.exe", "MHWNoChunk.exe"]
for tool in tools:
    tool_path = tools_dir / tool
    if tool_path.exists():
        print(f"  ✅ {tool} encontrado")
    else:
        print(f"  ❌ {tool} NÃO encontrado")

print(f"\n📍 Coloque as ferramentas em: {tools_dir}")
print("\nDownloads:")
print("  - WorldChunkTool: https://github.com/mhvuze/WorldChunkTool/releases")
print("  - MHWNoChunk: https://www.nexusmods.com/monsterhunterworld/mods/411")
