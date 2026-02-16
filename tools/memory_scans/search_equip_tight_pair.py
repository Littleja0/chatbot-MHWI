import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

# IDs equipados (Master Rank)
id_head = 1457
id_chest = 1463

print(f"Buscando Elmo {id_head} e Peito {id_chest} juntos...")

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found_total = 0

byte_head = struct.pack('<I', id_head)
byte_chest = struct.pack('<I', id_chest)

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(byte_head)
            while idx != -1:
                # Checar se Peito esta perto (geralmente depois)
                # Tentamos dar um range de 200 bytes
                sub = data[idx : idx + 200]
                if byte_chest in sub:
                    chest_off = sub.find(byte_chest)
                    others = [884, 1155, 1466, 6]
                    found_others = []
                    for o in others:
                        if struct.pack('<I', o) in sub:
                            found_others.append(o)
                    
                    if len(found_others) >= 2:
                        abs_addr = mbi.BaseAddress + idx
                        print(f"  PAREAR ENCONTRADO em {hex(abs_addr)}! Peito em +{hex(chest_off)}")
                        print(f"    Outros IDs no bloco: {found_others}")
                        
                        # DUMP do bloco
                        print("    Dump:")
                        for d in range(0, 0x80, 4):
                            v = struct.unpack('<I', sub[d:d+4])[0] if d < len(sub)-4 else 0
                            print(f"      +{hex(d)}: {v}")
                        
                        found_total += 1
                
                idx = data.find(byte_head, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nBusca concluida. Total: {found_total}")
