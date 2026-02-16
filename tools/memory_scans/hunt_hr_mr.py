import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

# HR 54, MR 10
target_bytes = struct.pack('<II', 54, 10)

print(f"Buscando [HR 54, MR 10] na RAM...")

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
            idx = data.find(target_bytes)
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                found.append(abs_addr)
                print(f"  Encontrado [54, 10] em {hex(abs_addr)}")
                idx = data.find(target_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

for a in found:
    print(f"\nExplorando struct em {hex(a)}:")
    # Se HR/MR estão em a, vamos olhar -0x100 a +0x400
    try:
        struct_data = pm.read_bytes(a - 0x100, 0x500)
        # Buscar ID da arma (779 ou 2103)
        for j in range(0, len(struct_data)-4):
            val = struct.unpack('<I', struct_data[j:j+4])[0]
            if val in [779, 2103, 2738]:
                print(f"    🎯 ARMA ATIVA ID {val} ENCONTRADA em {hex(a - 0x100 + j)}")
                print(f"    Offset relativo ao HR: {hex(-0x100 + j)}")
    except: pass
