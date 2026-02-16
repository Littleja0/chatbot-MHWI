import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# Ponto de referência: Long Sword (Tipo 3)
ls_offset = 0x2F185DC
addr = base + ls_offset

print(f"Dumping Weapon ID Array around {hex(addr)}...")
# Vamos checar 20 slots antes e 20 depois (cada slot = 4 bytes)
for i in range(-14, 15):
    val = pm.read_int(addr + (i * 4))
    print(f"  Slot {i:+03d} (Offset {hex(ls_offset + i*4)}): {val}")
