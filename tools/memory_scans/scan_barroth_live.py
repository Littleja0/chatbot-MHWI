import sys, struct
from pymem import Pymem

pm = Pymem('MonsterHunterWorld.exe')

target_id = 2224 # Fatiador de Barroth I
target_bytes = struct.pack('<I', target_id)

print(f"Buscando ID {target_id} na memória RAM...")

def scan():
    # Vamos focar na região do save/player (em volta de 0x90000000 como vimos nos logs)
    # Mas vamos fazer um scan mais amplo
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
            if mbi.RegionSize < 50 * 1024 * 1024:
                try:
                    data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                    idx = data.find(target_bytes)
                    while idx != -1:
                        p_addr = mbi.BaseAddress + idx
                        # Ver se tem o TIPO (1) perto
                        # No MHW, o tipo costuma vir ANTES ou DEPOIS do ID
                        type_before = struct.unpack('<I', data[idx-4:idx])[0] if idx >= 4 else -1
                        type_after = struct.unpack('<I', data[idx+4:idx+8])[0] if idx+8 <= len(data) else -1
                        
                        if type_before == 1 or type_after == 1:
                            print(f"  [FOUND] ID {target_id} + TIPO 1 em {hex(p_addr)}")
                            # Ver contexto (16 bytes antes e depois)
                            ctx = data[max(0, idx-16) : min(len(data), idx+16)]
                            print(f"     Contexto: {ctx.hex(' ')}")
                        
                        idx = data.find(target_bytes, idx + 1)
                except: pass
        addr = mbi.BaseAddress + mbi.RegionSize

if __name__ == "__main__":
    scan()
