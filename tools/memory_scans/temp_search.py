"""Scan dinâmico: encontra weapon ID no heap (dados que mudam)"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymem import Pymem
import struct, ctypes
from ctypes import wintypes

pm = Pymem("MonsterHunterWorld.exe")
base = pm.process_base.lpBaseOfDll
print(f"Base: {hex(base)}")

def rp(a):
    try: return pm.read_longlong(a)
    except: return None

def ri(a):
    try: return pm.read_int(a)
    except: return None

# Verificar se o offset antigo ainda tem 2103
old_val = ri(base + 0x2F185DC)
print(f"Offset antigo (0x2F185DC): {old_val} (se ainda for 2103, eh estatico!)")

# Ler o tipo de arma atual (esse funciona!)
weapon_ptr = rp(base + 0x050139A0)
step1 = rp(weapon_ptr + 0x50) if weapon_ptr else None
if step1:
    w1 = rp(step1 + 0xC0)
    if w1:
        w2 = rp(w1 + 0x8)
        if w2:
            w3 = rp(w2 + 0x78)
            if w3:
                wtype = ri(w3 + 0x2E8)
                WTYPES = {0:"GS",1:"SnS",2:"DB",3:"LS",4:"Hammer",5:"HH",
                          6:"Lance",7:"GL",8:"SA",9:"CB",10:"IG",11:"Bow",12:"HBG",13:"LBG"}
                print(f"Tipo de arma atual: {wtype} = {WTYPES.get(wtype, '?')}")
                
                # Scan ao redor do weapon type para achar weapon ID
                print(f"\nScanneando valores perto do weapon type ({hex(w3)}):")
                print(f"Offsets 0x0 a 0x2000 com valores 1-20000:")
                for off in range(0x0, 0x2000, 0x4):
                    val = ri(w3 + off)
                    if val is not None and 1 <= val <= 20000 and val != wtype:
                        print(f"  w3+{hex(off)}: {val}")

# Tentar via 0x98 (caminho do weapon ID original)
print(f"\nScanneando via step1+0x98 (caminho original do weapon ID):")
if step1:
    p98 = rp(step1 + 0x98)
    if p98:
        print(f"  step1+0x98 = {hex(p98)}")
        # Seguir sub-ponteiros
        for off1 in range(0x0, 0x100, 0x8):
            p1 = rp(p98 + off1)
            if p1 and p1 > 0x10000:
                for off2 in range(0x0, 0x100, 0x8):
                    p2 = rp(p1 + off2)
                    if p2 and p2 > 0x10000:
                        for off3 in range(0x0, 0x100, 0x8):
                            p3 = rp(p2 + off3)
                            if p3 and p3 > 0x10000:
                                # Scan para valores de weapon ID (100-20000)
                                for off4 in range(0x0, 0x2000, 0x4):
                                    val = ri(p3 + off4)
                                    if val is not None and 100 <= val <= 20000:
                                        print(f"  +{hex(off1)}->{hex(off2)}->{hex(off3)}->{hex(off4)}: {val}")

# Scan do WEAPON_DATA address
print(f"\nScanneando via WEAPON_DATA (0x05012080):")
wd_ptr = rp(base + 0x05012080)
if wd_ptr:
    print(f"  WEAPON_DATA ptr = {hex(wd_ptr)}")
    p2 = rp(wd_ptr + 0xC8)
    if p2:
        print(f"  +0xC8 = {hex(p2)}")
        for off in range(0x0, 0x2000, 0x4):
            val = ri(p2 + off)
            if val is not None and 100 <= val <= 20000:
                print(f"    p2+{hex(off)}: {val}")

print("\nBusca concluida!")
input("Pressione ENTER...")
