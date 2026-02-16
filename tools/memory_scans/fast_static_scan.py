import sys, struct
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll
size = pm.process_base.SizeOfImage

target_id = 2412
target_bytes = struct.pack('<I', target_id)

print(f"Buscando ID {target_id} no modulo base (0x{base:X}, tamanho: {size})...")

data = pm.read_bytes(base, size)
idx = data.find(target_bytes)
found_any = False

while idx != -1:
    found_any = True
    print(f"  ⭐ ENCONTRADO! Offset estático: base + {hex(idx)}")
    # Checar se o Tipo 4 está por perto
    try:
        nearby = data[idx-16 : idx+16]
        print(f"     Contexto (hex): {nearby.hex(' ')}")
    except: pass
    idx = data.find(target_bytes, idx + 4)

if not found_any:
    print("Não encontrado no módulo base. Tentando buscar o ID 2103 (Sabre) para comparar...")
    target_bytes = struct.pack('<I', 2103)
    idx = data.find(target_bytes)
    while idx != -1:
        print(f"  📍 Sabre (2103) achado em: base + {hex(idx)}")
        idx = data.find(target_bytes, idx + 4)
