import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

# Buscando o par [TIPO, ID]
# Hammer: Tipo 4, ID 779
# LS: Tipo 3, ID 2103
# CB: Tipo 9, ID 2738

search_pairs = [
    (4, 779),   # Hammer Gigagelo II
    (3, 2103),  # LS Sabre Oculto+
    (9, 2738),  # CB Fortaleza Cromada
    (5, 2490),  # HH Bardo Palácio
]

def scan_ram():
    k32 = ctypes.windll.kernel32
    addr = 0
    results = []
    
    while addr < 0x7FFFFFFFFFFF:
        mbi = MBI()
        if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
        if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}:
            try:
                data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                for wtype, wid in search_pairs:
                    # Tenta [WTYPE, WID]
                    target1 = struct.pack('<II', wtype, wid)
                    idx = data.find(target1)
                    while idx != -1:
                        print(f"  ⭐ PAR ENCONTRADO [Tipo {wtype}, ID {wid}] em {hex(mbi.BaseAddress + idx)}")
                        results.append((mbi.BaseAddress + idx, wtype, wid))
                        idx = data.find(target1, idx + 4)
                    
                    # Tenta [WID, WTYPE]
                    target2 = struct.pack('<II', wid, wtype)
                    idx = data.find(target2)
                    while idx != -1:
                        print(f"  ⭐ PAR ENCONTRADO [ID {wid}, Tipo {wtype}] em {hex(mbi.BaseAddress + idx)}")
                        results.append((mbi.BaseAddress + idx, wtype, wid))
                        idx = data.find(target2, idx + 4)
            except: pass
        addr = mbi.BaseAddress + mbi.RegionSize
    return results

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

print("Iniciando busca por pares [Tipo, ID] na RAM...")
scan_ram()
print("Busca concluída.")
