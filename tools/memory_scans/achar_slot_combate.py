import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

print("Buscando todas as instâncias de 'LittleJão' para achar o Slot de Combate...")

class MBI:
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.BaseAddress = ctypes.c_ulonglong()
        self.RegionSize = ctypes.c_ulonglong()
        self.State = wintypes.DWORD()
        self.Protect = wintypes.DWORD()

import ctypes
from ctypes import wintypes
class MBI_STRUCT(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found_slots = []

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI_STRUCT()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(b"LittleJ\xc3\xa3o") # UTF-8 para LittleJão
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                # Save data base é Nome - 0x50
                save_base = abs_addr - 0x50
                # O Tipo fica em base + 0x74
                try:
                    wtype = pm.read_int(save_base + 0x74)
                    print(f"  📍 Achado 'LittleJão' em {hex(save_base)} | Tipo em +0x74: {wtype}")
                    if 0 <= wtype <= 13:
                        # Checar se o ID em +0x78 ou +0x7C faz sentido (ID > 0)
                        wid = pm.read_int(save_base + 0x78)
                        print(f"     ID em +0x78: {wid}")
                except: pass
                idx = data.find(b"LittleJ\xc3\xa3o", idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize
