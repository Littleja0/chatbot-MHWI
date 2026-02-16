import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
player_addr = 0x95c5987c 

print(f"Buscando ponteiros no Player Struct ({hex(player_addr)})...")

try:
    data = pm.read_bytes(player_addr, 0x1000)
    for i in range(0, len(data)-8, 8):
        val = struct.unpack('<Q', data[i:i+8])[0]
        if 0x10000000 < val < 0x200000000: # Faixa comum de heap
            print(f"  Pointer at +{hex(i)}: {hex(val)}")
            # Checar o que tem lá
            try:
                content = pm.read_bytes(val, 0x10)
                ints = struct.unpack('<IIII', content)
                print(f"    Conteúdo: {ints}")
                if 2412 in ints:
                    print(f"    🎯 ACHADO PONTEIRO PARA ID 2412 em +{hex(i)}!")
            except: pass
except Exception as e:
    print(f"Erro: {e}")
