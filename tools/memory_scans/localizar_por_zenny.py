import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
zenny = 598959
zenny_bytes = struct.pack('<I', zenny)

print(f"Buscando Zenny ({zenny}) na RAM...")

import ctypes
from ctypes import wintypes
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
            idx = data.find(zenny_bytes)
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                print(f"  Encontrado Zenny em {hex(abs_addr)}")
                
                # O Zenny fica em SaveAddr + 0x98.
                # Então SaveAddr = abs_addr - 0x98.
                save_addr = abs_addr - 0x98
                # Testar se o nome está em +0x50
                try:
                    name = pm.read_bytes(save_addr + 0x50, 10).split(b'\x00')[0].decode('utf-8')
                    print(f"    ⭐ NOME ENCONTRADO: {name}")
                    if name == "LittleJão":
                        print(f"    ✅ SAVE DE LITTLEJÃO CONFIRMADO EM: {hex(save_addr)}")
                        # Agora vamos escanear este struct pelo ID da arma (779, 2103, 2738)
                        struct_data = pm.read_bytes(save_addr, 0x1000)
                        for i in range(0, 0x1000-4, 1):
                            val = struct.unpack('<I', struct_data[i:i+4])[0]
                            if val in [779, 2103, 2738]:
                                print(f"    🎯 ARMA ATIVA ENCONTRADA no struct + {hex(i)}: ID {val}")
                        
                        # Também checar Shorts
                        for i in range(0, 0x1000-2, 1):
                            val = struct.unpack('<H', struct_data[i:i+2])[0]
                            if val in [779, 2103, 2738]:
                                print(f"    🎯 ARMA ATIVA (SHORT) no struct + {hex(i)}: ID {val}")
                except: pass
                
                idx = data.find(zenny_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize
