import sys, struct
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
struct_addr = 0x95c598d0

targets = [1457, 1463, 884, 1155, 1466, 6]

print(f"Buscando IDs de equipamento dentro do Player Struct ({hex(struct_addr)})...")

# Scan 64KB around the struct
try:
    data = pm.read_bytes(struct_addr - 0x1000, 0x10000)
    for t in targets:
        target_bytes = struct.pack('<I', t)
        idx = data.find(target_bytes)
        while idx != -1:
            abs_addr = struct_addr - 0x1000 + idx
            rel = abs_addr - struct_addr
            print(f"  FOUND {t} at struct {rel:+06x}")
            idx = data.find(target_bytes, idx + 4)
except Exception as e:
    print(f"Error: {e}")
