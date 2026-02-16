import sys, struct, ctypes
from ctypes import wintypes
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong), ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wintypes.DWORD), ("PartitionId", wintypes.WORD),
                ("RegionSize", ctypes.c_ulonglong), ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

k32 = ctypes.windll.kernel32
addr = 0
found = []

print("Buscando 'LittleJ' em toda a RAM...")

while addr < 0x7FFFFFFFFFFF:
    mbi = MBI()
    if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0: break
    if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x08}:
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            idx = data.find(b"LittleJ\x00")
            while idx != -1:
                abs_addr = mbi.BaseAddress + idx
                found.append(abs_addr)
                print(f"  Encontrado em {hex(abs_addr)}")
                idx = data.find(b"LittleJ\x00", idx + 4)
        except: pass
    addr = mbi.BaseAddress + mbi.RegionSize

for a in found:
    print(f"\nVerificando arredores de {hex(a)}:")
    # HR costuma estar a -0x28 do nome, ou +0x40? Depende da versão.
    # Vamos ler -0x100 a +0x100
    try:
        context = pm.read_bytes(a - 0x100, 0x200)
        # Search for HR 54 and MR 10
        # 54 is hex 36, 10 is hex 0A
        for i in range(0, len(context)-4):
            val = struct.unpack('<I', context[i:i+4])[0]
            if val == 54:
                 # Check if next int is 10
                 next_val = struct.unpack('<I', context[i+4:i+8])[0]
                 if next_val == 10:
                     print(f"  ⭐ SAVE STRUCT PROVAVEL! HR=54 em {hex(a - 0x100 + i)}")
                     # O endereço base do save costuma ser o nome - 0x50
                     print(f"  Use base_addr = {hex(a - 0x50)}")
    except: pass
