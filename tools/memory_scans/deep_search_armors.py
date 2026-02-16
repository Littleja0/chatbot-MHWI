import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

TARGET_HEAD = 1457 # Cabelo de Oolong
target_bytes = struct.pack('<I', TARGET_HEAD)

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found = []

print(f"Buscando ID {TARGET_HEAD} (Oolong) em toda a memoria...")

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(target_bytes)
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                print(f"  FOUND {TARGET_HEAD} at {hex(abs_addr)}")
                
                # Check neighbors for other armors
                others = [1463, 884, 1155, 1466, 6]
                for d in range(-0x100, 0x200, 4):
                    try:
                        v = struct.unpack('<I', data[idx+d : idx+d+4])[0] if 0 <= idx+d < len(data)-4 else 0
                        if v in others:
                            print(f"    Neighbor {v} at head+{hex(d)}")
                    except: pass
                
                found.append(abs_addr)
                idx = data.find(target_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nTotal: {len(found)}")
