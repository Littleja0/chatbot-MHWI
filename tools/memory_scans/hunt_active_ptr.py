import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

def follow(b_addr, offsets):
    try:
        addr = pm.read_longlong(b_addr)
        for o in offsets[:-1]:
            addr = pm.read_longlong(addr + o)
            if not addr: return 0
        return addr + offsets[-1]
    except: return 0

# Pointer chain para o objeto da arma
weapon_ptr = follow(base + 0x050139A0, [0x50, 0xC0, 0x8, 0x78])

if weapon_ptr:
    print(f"Weapon Object: {hex(weapon_ptr)}")
    # Dump 0x2A0 to 0x300
    buff = pm.read_bytes(weapon_ptr + 0x2A0, 0x100)
    for i in range(0, 0x100, 8):
        val = struct.unpack('<Q', buff[i:i+8])[0]
        print(f"  +{hex(0x2A0 + i)}: {hex(val)}")
        
        # Testar se esse valor é um ponteiro para o ID 2412
        if 0x10000000 < val < 0x7FFFFFFFFFFF:
            try:
                # Checar o conteúdo do ponteiro
                content = pm.read_bytes(val, 0x20)
                ints = struct.unpack('<IIIIIIII', content)
                if 2412 in ints:
                    print(f"    🎯 PONTEIRO PARA ARMA ATIVA ACHADO em {hex(weapon_ptr + 0x2A0 + i)}")
                    print(f"    Conteúdo: {ints}")
            except: pass
else:
    print("Arma nao encontrada.")
