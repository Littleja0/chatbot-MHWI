import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# O usuário está com Hammer (4, Maça Palácio ID 2412)
current_type = 4
target_id = 2412

print(f"Buscando Slot Ativo [Tipo {current_type}, ID {target_id}] na região 0x5... e 0x6...")

# A região 0x50000000 - 0x70000000 é comum para heap objects de equipamentos
start = 0x10000000
end = 0xA0000000

found = []
for addr in range(start, end, 0x10000):
    try:
        data = pm.read_bytes(addr, 0x10000)
        # Procurar o padrão Tipo(4bytes), ID(4bytes) ou ID(4bytes), Tipo(4bytes)
        p1 = struct.pack('<II', current_type, target_id)
        idx = data.find(p1)
        while idx != -1:
            abs_addr = addr + idx
            print(f"  ⭐ BLOCO EQUIPADO ENCONTRADO em {hex(abs_addr)} [T+ID]")
            found.append(abs_addr)
            idx = data.find(p1, idx + 4)
            
        p2 = struct.pack('<II', target_id, current_type)
        idx = data.find(p2)
        while idx != -1:
            abs_addr = addr + idx
            print(f"  ⭐ BLOCO EQUIPADO ENCONTRADO em {hex(abs_addr)} [ID+T]")
            found.append(abs_addr)
            idx = data.find(p2, idx + 4)
    except: pass

print("\nAgora buscando ponteiros que apontam para esses blocos...")
for mbi_addr in range(0x100000000, 0x200000000, 0x10000): # Busca em endereços 64-bit
    try:
        data = pm.read_bytes(mbi_addr, 0x10000)
        for target in found:
            t_bytes = struct.pack('<Q', target)
            idx = data.find(t_bytes)
            while idx != -1:
                print(f"  🔗 PONTEIRO em {hex(mbi_addr + idx)} -> {hex(target)}")
                idx = data.find(t_bytes, idx + 8)
    except: pass
