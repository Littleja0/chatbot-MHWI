from pymem import Pymem
import struct

pm = Pymem('MonsterHunterWorld.exe')
name = b"LittleJ\xc3\xa3o"

print("Buscando TODAS as instâncias de LittleJão...")

def find_all():
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
        if k32.VirtualQueryEx(pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x20, 0x40}:
            try:
                data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                idx = data.find(name)
                while idx != -1:
                    p_addr = mbi.BaseAddress + idx
                    # Ver o que tem perto de cada LittleJão
                    # Um deles é o Save (já achamos). Outro é o PLAYER OBJ (o que importa).
                    # O PLAYER OBJ costuma ter pointers pra armas logo abaixo.
                    w_id = struct.unpack('<I', pm.read_bytes(p_addr + 0x74, 4))[0] if p_addr + 0x74 < 0x7FFFFFFFFFFF else -1
                    print(f"Encontrado em {hex(p_addr)} | Valor a +0x74: {w_id}")
                    idx = data.find(name, idx + 1)
            except: pass
        addr = mbi.BaseAddress + mbi.RegionSize

if __name__ == "__main__":
    find_all()
