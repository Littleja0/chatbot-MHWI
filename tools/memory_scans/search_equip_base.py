import sys, struct
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

targets = [1457, 1463, 884, 1155, 1466, 6]
target_bytes = struct.pack('<I', targets[0])

print(f"Buscando ID {targets[0]} no modulo base...")

# Scan range typically used for save data in base module
start = base + 0x2000000
limit = base + 0x6000000

offset = 0x2000000
while offset < 0x6000000:
    try:
        data = pm.read_bytes(base + offset, 0x100000)
        idx = data.find(target_bytes)
        while idx != -1:
            abs_off = offset + idx
            
            # Checar vizinhanca (+/- 0x100)
            matches = []
            for d in range(-0x100, 0x100, 4):
                try:
                    v = struct.unpack('<I', data[idx+d : idx+d+4])[0] if 0 <= idx+d < len(data)-4 else 0
                    if v in targets:
                        matches.append((d, v))
                except: pass
            
            if len(set(v for d, v in matches)) >= 4:
                print(f"  FOUND EQUIP BLOCK at base + {hex(abs_off)}")
                for d, v in matches:
                    print(f"    Offset {hex(d)}: ID {v}")
            
            idx = data.find(target_bytes, idx + 4)
        offset += 0x100000
    except:
        offset += 0x100000

print("\nBusca concluida.")
