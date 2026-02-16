import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

palaces = {
    0: 2080, 1: 2244, 2: 2328, 3: 2163, 4: 2412, 
    5: 2490, 6: 2569, 7: 2648, 8: 2731, 9: 2804, 
    10: 2884, 11: 3108, 12: 3030, 13: 2961
}

print("Mapeamento Final dos 14 Offsets Fixos:")
final_mapping = {}

# Scan ranges identified as containing weapon IDs
ranges = [
    (0x2F185A0, 0x2F18650), # LS range
    (0x35EC500, 0x35EDF00), # Palace and Starters range
    (0x3EABA00, 0x3EAC000), # Hammer Palace location?
]

for start_off, end_off in ranges:
    for addr in range(base + start_off, base + end_off, 4):
        val = pm.read_int(addr)
        for t, pid in palaces.items():
            if val == pid:
                final_mapping[t] = addr - base
                print(f"  Tipo {t} ({pid}): base + {hex(addr - base)}")

# Starter IDs (as fallback for those not yet equipped)
starters = {0: 1, 1: 125, 2: 236, 3: 89, 4: 345, 5: 442, 6: 514, 7: 605, 8: 694, 9: 757, 10: 831, 11: 1075, 12: 1004, 13: 924}
for start_off, end_off in ranges:
    for addr in range(base + start_off, base + end_off, 4):
        val = pm.read_int(addr)
        for t, sid in starters.items():
            if val == sid and t not in final_mapping:
                final_mapping[t] = addr - base
                print(f"  Tipo {t} (Starter {sid}): base + {hex(addr - base)} (Backup)")

print("\nDICIONARIO FINAL PARA O CÓDIGO:")
print(final_mapping)
