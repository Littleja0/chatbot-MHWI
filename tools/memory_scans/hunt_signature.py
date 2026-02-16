import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

# Padrao: Tipo(4) seguido de ID(2412) ou ID(2412) seguido de Tipo(4)
# 2412 em hex é 0x96C -> \x6C\x09\x00\x00
# 4 em hex é 0x04 -> \x04\x00\x00\x00

pattern1 = struct.pack('<II', 4, 2412) # [Tipo, ID]
pattern2 = struct.pack('<II', 2412, 4) # [ID, Tipo]

print("Buscando assinatura de combate [Tipo 4, ID 2412]...")

import ctypes
from ctypes import wintypes
class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found = []

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(pattern1)
            while idx != -1:
                print(f"  🔥 ASSINATURA [Tipo, ID] ACHADA em {hex(mbi.BaseAddress + idx)}")
                found.append(mbi.BaseAddress + idx)
                idx = data.find(pattern1, idx + 4)
                
            idx = data.find(pattern2)
            while idx != -1:
                print(f"  🔥 ASSINATURA [ID, Tipo] ACHADA em {hex(mbi.BaseAddress + idx)}")
                found.append(mbi.BaseAddress + idx)
                idx = data.find(pattern2, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nBusca concluída. {len(found)} locais achados.")
