import sqlite3, sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

# 1. Pegar IDs no banco
conn = sqlite3.connect('backend/mhw.db')
cur = conn.cursor()

names = ["%Gigagelo II%", "%Fortaleza Cromada%", "%Sabre Oculto+%", "%Maça Palácio%"]
target_ids = {}

for name in names:
    cur.execute("SELECT id, name FROM weapon_text WHERE name LIKE ? AND lang_id='pt'", (name,))
    row = cur.fetchone()
    if row: target_ids[row[0]] = row[1]

print(f"IDs Alvo: {target_ids}")

# 2. Escanear Memória RAM Total para esses IDs
pm = Pymem('MonsterHunterWorld.exe')
print("Iniciando Escaneamento Geral da RAM (Isso pode levar alguns segundos)...")

import ctypes
from ctypes import wintypes
class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found_locations = []

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}: # Read/Write
        try:
            region_data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            for tid, tname in target_ids.items():
                t_bytes = struct.pack('<I', tid)
                idx = region_data.find(t_bytes)
                while idx != -1:
                    abs_addr = mbi.BaseAddress + idx
                    found_locations.append((abs_addr, tid, tname))
                    print(f"  🔍 Encontrado {tname} (ID {tid}) em {hex(abs_addr)}")
                    idx = region_data.find(t_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"\nTotal de locais encontrados: {len(found_locations)}")
conn.close()
