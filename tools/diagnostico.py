"""
Diagnóstico v5 — Pattern Scan + UTF-16 + Busca ampla
Busca "LittleJao" em UTF-8 e UTF-16 em toda a memória.
Depois busca HR=54 e MR=9 ao redor do nome.
Execute como ADMINISTRADOR com o save carregado!
"""
from pymem import Pymem
import ctypes
from ctypes import wintypes
import struct

pm = Pymem("MonsterHunterWorld.exe")
base = pm.process_base.lpBaseOfDll
print(f"✅ Conectado! Base: {hex(base)}")
print(f"   Handle: {pm.process_handle}")

def ri(addr):
    try: return pm.read_int(addr)
    except: return None

def rs(addr, l=64):
    try:
        raw = pm.read_bytes(addr, l)
        return raw.split(b'\x00')[0].decode('utf-8', errors='ignore')
    except: return None

HR_REAL = 54
MR_REAL = 9
NAME = "LittleJao"
NAME_UTF8 = NAME.encode('utf-8')
NAME_UTF16 = NAME.encode('utf-16-le')

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_ulonglong),
        ("AllocationBase", ctypes.c_ulonglong),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_ulonglong),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]

MEM_COMMIT = 0x1000
kernel32 = ctypes.windll.kernel32
handle = pm.process_handle

# Protections que contêm dados legíveis
READABLE_PROTECTIONS = {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}

print(f"\n{'='*60}")
print(f"BUSCANDO '{NAME}' em toda a memória do processo...")
print(f"  UTF-8:  {NAME_UTF8.hex()}")
print(f"  UTF-16: {NAME_UTF16.hex()}")
print(f"{'='*60}")

addr = 0
regions = 0
found_utf8 = []
found_utf16 = []

while addr < 0x7FFFFFFFFFFF:
    mbi = MEMORY_BASIC_INFORMATION()
    result = kernel32.VirtualQueryEx(handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
    
    if result == 0:
        break
    
    if (mbi.State == MEM_COMMIT and 
        mbi.Protect in READABLE_PROTECTIONS and
        mbi.RegionSize > 0 and 
        mbi.RegionSize < 500 * 1024 * 1024):
        
        regions += 1
        try:
            data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
            
            # UTF-8 search
            start = 0
            while True:
                idx = data.find(NAME_UTF8, start)
                if idx == -1:
                    break
                abs_addr = mbi.BaseAddress + idx
                found_utf8.append(abs_addr)
                print(f"   🎯 UTF-8  em {hex(abs_addr)}")
                start = idx + 1
            
            # UTF-16 search
            start = 0
            while True:
                idx = data.find(NAME_UTF16, start)
                if idx == -1:
                    break
                abs_addr = mbi.BaseAddress + idx
                found_utf16.append(abs_addr)
                print(f"   🎯 UTF-16 em {hex(abs_addr)}")
                start = idx + 1
                
            # Também buscar apenas "Little" como fallback
            if not found_utf8 and not found_utf16:
                start = 0
                little_bytes = b"Little"
                count = 0
                while count < 3:
                    idx = data.find(little_bytes, start)
                    if idx == -1:
                        break
                    # Verificar se seguido por "Jao" ou "J"
                    context = data[idx:idx+20]
                    abs_addr = mbi.BaseAddress + idx
                    try:
                        text = context.split(b'\x00')[0].decode('utf-8', errors='ignore')
                    except:
                        text = ""
                    if len(text) > 6:  # Mais que "Little"
                        print(f"   📌 'Little...' em {hex(abs_addr)}: '{text}'")
                        if "Jao" in text or "jao" in text:
                            found_utf8.append(abs_addr)
                    count += 1
                    start = idx + 1
        except:
            pass
    
    next_addr = mbi.BaseAddress + mbi.RegionSize
    if next_addr <= addr:
        break
    addr = next_addr

print(f"\nRegiões escaneadas: {regions}")
print(f"UTF-8  encontrado: {len(found_utf8)} vezes")
print(f"UTF-16 encontrado: {len(found_utf16)} vezes")

# ============================================
# ANÁLISE AO REDOR DOS NOMES ENCONTRADOS
# ============================================
all_found = [(a, "UTF-8") for a in found_utf8] + [(a, "UTF-16") for a in found_utf16]

if all_found:
    print(f"\n{'='*60}")
    print("ANALISANDO VIZINHANÇA DOS NOMES ENCONTRADOS")
    print(f"{'='*60}")
    
    for name_addr, encoding in all_found[:10]:  # Max 10
        print(f"\n--- Nome em {hex(name_addr)} ({encoding}) ---")
        print(f"Buscando HR={HR_REAL} e MR={MR_REAL} em -0x2000 a +0x2000:")
        
        hr_locations = []
        mr_locations = []
        
        for delta in range(-0x2000, 0x2000, 0x4):
            val = ri(name_addr + delta)
            if val == HR_REAL:
                hr_locations.append(delta)
            if val == MR_REAL:
                mr_locations.append(delta)
        
        if hr_locations:
            print(f"   ⭐ HR={HR_REAL} encontrado nos offsets: {[hex(d) for d in hr_locations]}")
        else:
            print(f"   ❌ HR={HR_REAL} não encontrado perto do nome")
        
        if mr_locations:
            print(f"   ⭐ MR={MR_REAL} encontrado nos offsets: {[hex(d) for d in mr_locations]}")
        else:
            print(f"   ❌ MR={MR_REAL} não encontrado perto do nome")
        
        # Procurar pares HR+MR adjacentes ou próximos
        for hr_off in hr_locations:
            for mr_off in mr_locations:
                gap = abs(hr_off - mr_off)
                if gap <= 0x10:  # Dentro de 16 bytes
                    print(f"   ⭐⭐⭐ PAR ENCONTRADO! HR em nome+{hex(hr_off)}, MR em nome+{hex(mr_off)} (gap: {gap} bytes)")
        
        # Mostrar todos os valores "interessantes" (1-999) perto do nome
        print(f"\n   Valores 10-999 perto do nome (-0x100 a +0x200):")
        for delta in range(-0x100, 0x200, 0x4):
            val = ri(name_addr + delta)
            if val is not None and 10 <= val <= 999:
                marker = ""
                if val == HR_REAL: marker = " ⭐HR"
                if val == MR_REAL: marker = " ⭐MR"
                print(f"   nome+{hex(delta):>8}: {val}{marker}")
else:
    print("\n❌ NOME NÃO ENCONTRADO EM NENHUM FORMATO!")
    print("Possíveis causas:")
    print("  1. O jogo pode criptografar o nome na memória")
    print("  2. O nome pode ser armazenado em uma região protegida")
    print("  3. Tente digitar o nome exato do personagem (case-sensitive)")
    
    # Fallback: buscar diretamente HR=54 em regiões de dados
    print(f"\n{'='*60}")
    print("FALLBACK: Buscando HR=54 seguido de MR=9 em heap...")
    print(f"{'='*60}")
    
    addr = 0
    pairs_found = 0
    while addr < 0x7FFFFFFFFFFF and pairs_found < 20:
        mbi = MEMORY_BASIC_INFORMATION()
        result = kernel32.VirtualQueryEx(handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if result == 0:
            break
        
        if (mbi.State == MEM_COMMIT and 
            mbi.Protect in READABLE_PROTECTIONS and
            0 < mbi.RegionSize < 100 * 1024 * 1024):
            try:
                data = pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                # Buscar bytes de HR=54 (0x36000000 em little-endian int32)
                hr_bytes = struct.pack('<i', HR_REAL)
                mr_bytes = struct.pack('<i', MR_REAL)
                
                start = 0
                while start < len(data) - 8:
                    idx = data.find(hr_bytes, start)
                    if idx == -1:
                        break
                    # Verificar se MR=9 está logo ao lado (+4 ou -4)
                    if idx + 4 < len(data):
                        next_val = struct.unpack('<i', data[idx+4:idx+8])[0]
                        if next_val == MR_REAL:
                            abs_addr = mbi.BaseAddress + idx
                            print(f"   ⭐⭐ HR({HR_REAL})+MR({MR_REAL}) em {hex(abs_addr)} (região {hex(mbi.BaseAddress)})")
                            pairs_found += 1
                    if idx >= 4:
                        prev_val = struct.unpack('<i', data[idx-4:idx])[0]
                        if prev_val == MR_REAL:
                            abs_addr = mbi.BaseAddress + idx - 4
                            print(f"   ⭐⭐ MR({MR_REAL})+HR({HR_REAL}) em {hex(abs_addr)} (região {hex(mbi.BaseAddress)})")
                            pairs_found += 1
                    start = idx + 4
            except:
                pass
        
        next_addr = mbi.BaseAddress + mbi.RegionSize
        if next_addr <= addr:
            break
        addr = next_addr
    
    if pairs_found == 0:
        print("   ❌ Nenhum par HR+MR adjacente encontrado no heap")

print(f"\n✅ Diagnóstico v5 concluído!")
input("\nPressione ENTER para fechar...")
