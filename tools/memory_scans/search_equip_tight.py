import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

# IDs equipados
targets = [1457, 1463, 884, 1155, 1466, 6]

print(f"Buscando array de IDs (short) {targets}...")

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found_total = 0

# Testar buscas por short e por int
target_short = struct.pack('<HHHHH', 1457, 1463, 884, 1155, 1466)
target_int = struct.pack('<IIIII', 1457, 1463, 884, 1155, 1466)

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            
            # Buscar Short
            idx = data.find(target_short)
            while idx != -1:
                print(f"  FOUND (Short Array) at {hex(mbi.BaseAddress + idx)}")
                found_total += 1
                idx = data.find(target_short, idx + 2)
                
            # Buscar Int
            idx = data.find(target_int)
            while idx != -1:
                print(f"  FOUND (Int Array) at {hex(mbi.BaseAddress + idx)}")
                found_total += 1
                idx = data.find(target_int, idx + 4)
                
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nBusca concluida. Total: {found_total}")
