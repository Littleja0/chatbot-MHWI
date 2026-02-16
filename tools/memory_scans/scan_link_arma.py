import sys, struct
from pymem import Pymem

if sys.platform == "win32":
    try: sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    except: pass

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# O usuário está com Maça Palácio (ID 2412)
target_id = 2412

# Queremos achar esse ID 2412 em um lugar que mude se ele trocar de arma
# Vamos escanear a RAM e ver qual endereço do 2412 é "apontado" pelo objeto da arma (0x2b9517f68)
weapon_obj = 0x2b9517f68 

print(f"Buscando ID {target_id} e vendo se o objeto da arma aponta para ele...")

# Pegar todos os locais do ID 2412 na memória
# Para economizar tempo, vamos focar em regiões de Heap (0x10000000+)
import ctypes
from ctypes import wintypes
class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found_ids = []

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(struct.pack('<I', target_id))
            while idx != -1:
                found_ids.append(mbi.BaseAddress + idx)
                idx = data.find(struct.pack('<I', target_id), idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"Encontrados {len(found_ids)} locais com o ID {target_id}. Verificando se o objeto da arma tem ponteiros para eles...")

# Agora vasculhamos o objeto da arma (weapon_obj) em busca de ponteiros para esses IDs
weapon_data = pm.read_bytes(weapon_obj, 0x10000)
for i in range(0, 0x10000-8, 8):
    ptr = struct.unpack('<Q', weapon_data[i:i+8])[0]
    for target_addr in found_ids:
        # Se o ponteiro aponta para um lugar que contém o ID, ou perto dele
        if abs(ptr - target_addr) < 0x100:
            print(f"  ⭐ ACHADO! O objeto da arma em +{hex(i)} aponta para {hex(ptr)}, que contém o ID!")
            # Vamos ler esse ID
            try:
                real_id = pm.read_int(ptr) # Se o ptr for direto pro ID
                print(f"     ID lido diretamente: {real_id}")
            except: pass
