import sys
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

off = 0x35EC980
val = pm.read_int(base + off)
print(f"Valor no offset HH (0x35EC980): {val}")

# E no offset do Martelo (0x3EABA90)?
off_hammer = 0x3EABA90
try:
    val_hammer = pm.read_int(base + off_hammer)
    print(f"Valor no offset Martelo (0x3EABA90): {val_hammer}")
except: pass
