import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# 1. Pegar o TIPO que o jogo diz que está na mão agora (via Live Pointer)
def follow(b_addr, offsets):
    try:
        addr = pm.read_longlong(b_addr)
        for o in offsets[:-1]:
            addr = pm.read_longlong(addr + o)
            if not addr: return 0
        return addr + offsets[-1]
    except: return 0

# Pointer chain da arma
live_type_addr = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78, 0x2E8])
current_type = pm.read_int(live_type_addr) if live_type_addr else -1

print(f"Tipo de arma detectado na mão (Live): {current_type}")

# 2. Buscar onde esse Tipo e os IDs aparecem juntos
# Se tiver de Martelo (4), o ID deve ser 779 ou 2412
# Se tiver de LS (3), o ID deve ser 2103
targets = {779: 4, 2103: 3, 2738: 9, 2412: 4, 2804: 9, 2244: 1, 2490: 5}

print("Buscando o Slot de Equipamento Ativo...")
# Vamos escanear a RAM procurando o ID atual que bate com o Tipo atual
for addr in range(0x10000000, 0x100000000, 0x10000):
    try:
        data = pm.read_bytes(addr, 0x10000)
        for wid, wtype in targets.items():
            if wtype == current_type:
                t_bytes = struct.pack('<I', wid)
                idx = data.find(t_bytes)
                while idx != -1:
                    # Achamos o ID que bate com o tipo na mão!
                    # Vamos ver se o tipo está por perto (frequentemente a -4 ou +4 do ID)
                    abs_addr = addr + idx
                    val_before = struct.unpack('<I', data[max(0, idx-4):max(0, idx-4)+4])[0]
                    val_after = struct.unpack('<I', data[min(len(data)-4, idx+4):min(len(data)-4, idx+4)+4])[0]
                    
                    if val_before == current_type or val_after == current_type:
                        print(f"  ⭐ SLOT EQUIPADO ENCONTRADO! ID {wid} e Tipo {wtype} juntos em {hex(abs_addr)}")
                    
                    idx = data.find(t_bytes, idx + 4)
    except: pass
