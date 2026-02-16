import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

# IDs equipados (do print e do db)
targets = [1457, 1463, 884, 1155, 1466, 6]

print(f"Buscando combinacao de IDs {targets}...")

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found_total = 0

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            # Buscar primeiro ID (Oolong head)
            target = struct.pack('<I', targets[0])
            idx = data.find(target)
            while idx != -1:
                potential_base = mbi.BaseAddress + idx
                
                # Checar vizinhanca (+/- 0x1000) por outros IDs
                counts = 0
                matches = []
                for d in range(-0x200, 0x400, 4):
                    try:
                        v = struct.unpack('<I', data[idx+d : idx+d+4])[0] if 0 <= idx+d < len(data)-4 else 0
                        if v in targets:
                            counts += 1
                            matches.append((d, v))
                    except: pass
                
                # Se achou pelo menos 4 dos 6 IDs, é um candidato forte
                unique_found = len(set(v for d, v in matches))
                if unique_found >= 4:
                    print(f"\nCANDIDATO em {hex(potential_base)}:")
                    for d, v in matches:
                        print(f"  Offset {hex(d)}: ID {v}")
                    found_total += 1
                
                idx = data.find(target, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nBusca concluida. Total de candidatos: {found_total}")
