import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

# Buscando o valor 1 (Espada e Escudo) que o usuário está usando agora
target = 1
target_bytes = struct.pack('<I', target)

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found = []

print("Buscando possiveis enderecos de Weapon Type (1)...")

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}: # Read/Write
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(target_bytes)
            while idx != -1:
                # Checar se o ID de uma SnS está por perto
                # Se ele tiver uma SnS equipada, o ID deve estar perto do tipo
                # IDs de SnS costumam ser > 0
                found.append(mbi.BaseAddress + idx)
                idx = data.find(target_bytes, idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

print(f"Encontrados {len(found)} enderecos com valor '1'.")
# Vamos checar os primeiros 10 e ver se algum tem o nome LittleJão por perto (indicando Player Struct)
for a in found[:20]:
    try:
        # Check +/- 1KB
        nearby = pm.read_bytes(a - 0x200, 0x400)
        if b"LittleJ" in nearby:
            print(f"  ⭐ POTENCIAL: {hex(a)} esta perto do nome do jogador!")
    except: pass
