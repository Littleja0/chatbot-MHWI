import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# Vamos listar todos os ponteiros a partir de MonsterHunterWorld.exe + 0x050139A0 -> 0x50 -> 0x20
# E ver o que tem neles
root = pm.read_longlong(base + 0x050139A0)
root = pm.read_longlong(root + 0x50)
root = pm.read_longlong(root + 0x20)

print(f"Root (0x50 -> 0x20): {hex(root)}")

for offset in range(0, 0x1000, 8):
    try:
        ptr = pm.read_longlong(root + offset)
        if 0x10000000 < ptr < 0x7FFFFFFFFFFF:
            # Checar se esse objeto tem o tipo da arma em +0x2E8
            wtype = pm.read_int(ptr + 0x2E8)
            if 0 <= wtype <= 13:
                print(f"  ⭐ Candidato em root + {hex(offset)}: {hex(ptr)} (Tipo em +2E8: {wtype})")
                # Se o tipo bater com o que o usuário está usando (vamos supor 4 ou 3)
                # Escanear esse objeto por IDs
                obj_data = pm.read_bytes(ptr, 0x1000)
                for i in range(0, 0x1000-4, 4):
                    v = struct.unpack('<I', obj_data[i:i+4])[0]
                    if v in [779, 2103, 2738]:
                        print(f"    🎯 ID {v} ENCONTRADO em objeto + {hex(i)}")
    except: pass
