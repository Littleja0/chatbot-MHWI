import sys, struct
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')
base = pm.process_base.lpBaseOfDll

# IDs de 'Fatiador de Barroth I' e SnS
target_id = 2224 
target_type = 1

print(f"Buscando endereço vivo da arma {target_id}...")

def find_pointers_to(target_addr):
    # Scan for pointers to a specific address in the base module
    found = []
    import ctypes
    size = pm.process_base.SizeOfImage
    mod_data = pm.read_bytes(base, size)
    
    target_bytes = struct.pack('<Q', target_addr)
    idx = mod_data.find(target_bytes)
    while idx != -1:
        found.append(base + idx)
        idx = mod_data.find(target_bytes, idx + 1)
    return found

# 1. Achar o endereço da arma agora
target_bytes = struct.pack('<II', target_id, target_type)
data = pm.read_bytes(0x25a000000, 0x10000000) # Scan roughly in heap area
idx = data.find(target_bytes)
if idx != -1:
    live_addr = 0x25a000000 + idx
    print(f"Arma viva encontrada em {hex(live_addr)}")
    # Agora buscar quem aponta pra cá
    # (Pode demorar, vamos pular o global e olhar offsets conhecidos)
else:
    print("Não encontrei a arma ativa na área de heap esperada.")

if __name__ == "__main__":
    # Scan global for 2224 + 1
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
                chunk = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                i = chunk.find(target_bytes)
                if i != -1:
                    actual_addr = mbi.BaseAddress + i
                    print(f"!!! ARMA ENCONTRADA EM: {hex(actual_addr)}")
                    # Ver se 0x050139A0 aponta pra uma chain que chega aqui
            except: pass
        addr = mbi.BaseAddress + mbi.RegionSize
