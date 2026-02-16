import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

target_weapon = 2103
target_head = 1457

print(f"Buscando combinacao de Arma {target_weapon} e Elmo {target_head}...")

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
            w_bytes = struct.pack('<I', target_weapon)
            idx = data.find(w_bytes)
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                
                # Checar se tem o elmo 1457 por perto (+/- 0x5000)
                # O equipamento costuma ficar num bloco de uns 20KB
                search_range = 0x5000
                sub_data = data[max(0, idx-search_range) : min(len(data), idx+search_range)]
                if struct.pack('<I', target_head) in sub_data:
                    h_idx = sub_data.find(struct.pack('<I', target_head))
                    rel_h = h_idx - (idx if idx < search_range else search_range)
                    print(f"  FOUND! Arma em {hex(abs_addr)}, Elmo em offset {hex(rel_h)}")
                    
                    # Dump neighbors
                    print("  Neighbors of Arma:")
                    for d in range(-0x20, 0x100, 4):
                        try:
                            v = struct.unpack('<I', sub_data[h_idx+d : h_idx+d+4])[0]
                            print(f"    Elmo{hex(d)}: {v}")
                        except: pass
                        
                    found_total += 1
                
                idx = data.find(w_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nBusca concluida. Total: {found_total}")
