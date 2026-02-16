import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
struct_addr = 0x95c598d0

print(f"Dumping around suspected equipment block in struct...")
# Scanning from 0x250 to 0x2A0
for i in range(0x250, 0x2A0, 4):
    try:
        val = pm.read_int(struct_addr + i)
        print(f"  +{hex(i)}: {val}")
    except: pass
