import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')

# O usuário está com Maça Palácio (ID 2412, Tipo 4)
target_id = 2412
target_type = 4

print(f"Buscando ID {target_id} (Martelo) na RAM...")

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
            # Procurar par [Tipo 4, ID 2412] ou o ID 2412 sozinho
            t_bytes = struct.pack('<I', target_id)
            idx = data.find(t_bytes)
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                # Checar se o Tipo 4 está por perto (frequentemente a -4 ou +4)
                try:
                    nearby = pm.read_bytes(abs_addr - 16, 32)
                    context = struct.unpack('<IIIIIIII', nearby)
                    if 4 in context:
                        print(f"  ⭐ PAR ENCONTRADO! ID {target_id} e Tipo 4 próximos em {hex(abs_addr)}")
                        print(f"     Valores: {context}")
                except: pass
                idx = data.find(t_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print("Busca concluída.")
