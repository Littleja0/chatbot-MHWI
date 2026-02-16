import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

# Buscando o par [ID, TIPO] ou [TIPO, ID]
pairs = [
    (779, 4),   # Martelo Gigagelo
    (2103, 3),  # LS Sabre
    (2738, 9),  # CB Fortaleza
    (2490, 5),  # HH Bardo
]

print("Buscando pares ID/Tipo na RAM...")

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            for wid, wtype in pairs:
                p1 = struct.pack('<II', wid, wtype)
                idx = data.find(p1)
                while idx != -1:
                    print(f"  ⭐ ENCONTRADO [ID {wid}, Tipo {wtype}] em {hex(mbi.BaseAddress + idx)}")
                    idx = data.find(p1, idx + 4)
                
                p2 = struct.pack('<II', wtype, wid)
                idx = data.find(p2)
                while idx != -1:
                    print(f"  ⭐ ENCONTRADO [Tipo {wtype}, ID {wid}] em {hex(mbi.BaseAddress + idx)}")
                    idx = data.find(p2, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize
