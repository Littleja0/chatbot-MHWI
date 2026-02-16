import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
struct_addr = 0x95c598d0
base_addr = struct_addr + 0x278

print(f"Dumping around suspected charm offset {hex(base_addr)}...")
for i in range(-0x100, 0x100, 4):
    try:
        val = pm.read_int(base_addr + i)
        print(f"  {i:+04x}: {val}")
    except: pass
