import os

CHUNK_PATH = r"D:\Steam\steamapps\common\Monster Hunter World\chunk\chunkG0.bin"

if not os.path.exists(CHUNK_PATH):
    print(f"Nenhum chunk encontrado.")
    exit(1)

print(f"Lendo: {CHUNK_PATH}")
with open(CHUNK_PATH, "rb") as f:
    header = f.read(100)
    print(f"Hex: {header.hex()}")
    print(f"ASCII: {header}")
