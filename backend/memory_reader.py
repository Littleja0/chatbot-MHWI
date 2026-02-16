"""
memory_reader.py — Módulo de leitura de memória do MHW para o Chatbot.

Lê dados em tempo real do processo MonsterHunterWorld.exe usando Pymem.
Baseado nos endereços e offsets do HunterPie (v1).

Goals: Armas, Armaduras, Amuletos, Monstros, Abnormalities, Dano
Constraints: Sem overlays (exceto dano)
"""

import time
import threading
import sqlite3
import os
import sys
import struct
from typing import Optional, Dict, List, Any

try:
    from pymem import Pymem  # type: ignore
    from pymem.exception import ProcessNotFound, MemoryReadError  # type: ignore
    PYMEM_AVAILABLE = True
except ImportError:
    PYMEM_AVAILABLE = False
    print("[MEMORY] Pymem não encontrado. Instale com: pip install pymem")


# ============================================================
# ENDEREÇOS BASE (Relativos ao módulo MonsterHunterWorld.exe)
# ============================================================
ADDRESSES = {
    "WEAPON":           0x050139A0,
    "EQUIPMENT":        0x050139A0,
    "ABNORMALITY":      0x050139A0,
    "MONSTER":          0x051238C8,
    "MONSTER_LIST":     0x0500CF40,
    "DAMAGE":           0x051C46B8,
    "LEVEL":            0x05013950,
    "ZONE":             0x0500ECA0,
    "PARTY":            0x05013530,
    "SESSION":          0x051C46B8,
    "QUEST_DATA":       0x0500ED30,
    "WEAPON_DATA":      0x05012080,
    "WORLD_DATA":       0x05013830,
}

# ============================================================
# POINTER CHAINS (Offsets para navegar ponteiros)
# ============================================================
OFFSETS = {
    "WEAPON":               [0x50, 0xC0, 0x8, 0x78, 0x2E8],
    "WEAPON_ID":            [0x50, 0xC0, 0x8, 0x78, 0x2E8], # Reaproveitamos o tipo p/ achar ID via tabela
    "WEAPON_SHARPNESS":     [0x50, 0xC0, 0x8, 0x78, 0x2E8, 0x8, 0xA8], # Tentativa p/ afiação
    "EQUIPMENT":            [0x50, 0xC0, 0x8, 0x78, 0x2D0], # Offset live p/ equipamento
    "PLAYER_BASIC_INFO":    [0x50, 0x7630, 0x0],
    "LEVEL":                [0xA8],
    "ZONE":                 [0xAED0],
    "MONSTER":              [0x50, 0x76B0, 0x0, 0x138, 0x0],
    "MONSTER_LIST":         [0x38],
    "DAMAGE":               [0x258, 0x38, 0x450, 0x8, 0x48],
    "QUEST_DATA":           [0x50, 0x7630, 0x13180],
    "QUEST_TIMER":          [0x13180],
    "ABNORMALITY":          [0x50, 0x7D20, 0x0],
    "ABNORMALITY_GEAR":     [0x50, 0x12608, 0x0],
}


# Offsets relativos ao Smart Struct (SAVE DATA)
STRUCT_OFFSETS = {
    "HR": 0x40,
    "MR": 0x84,
    "ZENNY": 0x44,
    "NAME": 0x0,
}

# ============================================================
# CONSTANTES DO JOGO
# ============================================================
WEAPON_TYPES = {
    0: "Grande Espada",
    1: "Espada e Escudo",
    2: "Espada Dupla",
    3: "Espada Longa",
    4: "Martelo",
    5: "Lança de Caça",
    6: "Lança",
    7: "Lança-Canhão",
    8: "Espada-Machado",
    9: "Espadão de Carga",
    10: "Glaive de Inseto",
    11: "Arco",
    12: "Metralhadora Pesada",
    13: "Metralhadora Leve",
}

WEAPON_TYPES_EN = {
    0: "great-sword", 1: "sword-and-shield", 2: "dual-blades",
    3: "long-sword", 4: "hammer", 5: "hunting-horn",
    6: "lance", 7: "gunlance", 8: "switch-axe",
    9: "charge-blade", 10: "insect-glaive", 11: "bow",
    12: "heavy-bowgun", 13: "light-bowgun",
}

SHARPNESS_COLORS = ["Vermelho", "Laranja", "Amarelo", "Verde", "Azul", "Branco", "Roxo"]

# Mapeamento de offsets estáticos para IDs de armas por tipo
# Esses offsets são mais estáveis que as pointer chains em algumas sessões
# Mapeamento de offsets estáticos para IDs de armas por tipo
# Esses offsets são os ganchos fixos no MonsterHunterWorld.exe
WEAPON_ID_OFFSETS = {
    0:  0x3DE761E, # Great Sword
    1:  0x25A9608, # Sword and Shield (Palace SnS testado)
    2:  0x35ECB34, # Dual Blades (Machadinhas Beo testado)
    3:  0x2F185DC, # Long Sword (Sabre Oculto testado)
    4:  0x3EABAE0, # Hammer (Maça Palácio testado)
    5:  0x35EC980, # Hunting Horn
    6:  0x35EC8A0, # Lance
    7:  0x205A3B8, # Gunlance
    8:  0x35EC768, # Switch Axe
    9:  0x35EC6C8, # Charge Blade
    10: 0x35EC618, # Insect Glaive
    11: 0x35ED6B0, # Bow
    12: 0x35ED764, # HBG
    13: 0x35ED830, # LBG
}
DEFAULT_WEAPON_ID_OFFSET = 0x2F185DC

# Equipment slot sub-offsets (relativos ao endereço base do equipamento)
EQUIPMENT_SLOTS = {
    "head":  0x0,
    "chest": 0x4,
    "arms":  0x8,
    "waist": 0xC,
    "legs":  0x10,
    "charm": 0x14,
}

# Offsets internos da estrutura do monstro
MONSTER_STRUCT: Dict[str, int] = {
    "id":       0x12280,
    "hp":       0x7678,
    "max_hp":   0x7670,
    "size":     0x7730,
    "next":     0x0,
}

# Dano: cada player ocupa ~0x2A0 bytes
DAMAGE_PLAYER_STRIDE = 0x2A0
DAMAGE_NAME_OFFSET   = 0x0
DAMAGE_VALUE_OFFSET  = 0x48

# Abnormalities: offsets internos para consumíveis comuns
CONSUMABLE_BUFF_OFFSETS = {
    "Poção Demoníaca":      0x0,
    "Mega Poção Demoníaca": 0x4,
    "Semente Demoníaca":    0x8,
    "Pó Demoníaco":         0xC,
    "Garra Demoníaca":      0x10,
    "Poção de Armadura":    0x14,
    "Mega Poção de Armadura": 0x18,
    "Semente de Armadura":  0x1C,
    "Pó de Armadura":       0x20,
    "Pele Dura":            0x24,
}


# ============================================================
# UTILIDADE
# ============================================================
def is_admin() -> bool:
    """Verifica se o script está rodando como administrador."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[attr-defined]
    except Exception:
        return False


# ============================================================
# CLASSE PRINCIPAL
# ============================================================
class MHWMemoryReader:
    """Leitor de memória do Monster Hunter World: Iceborne."""

    def __init__(self) -> None:
        self.pm: Any = None
        self.base: int = 0
        self.connected: bool = False
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = {}
        self._cache_ts: float = 0
        self._cache_ttl: float = 0.5   # 500ms de cache
        
        # Endereço dinâmico do struct do jogador encontrado via scan
        self.player_struct_addr: int = 0
        # Timestamp do último scan profundo para evitar lag
        self._last_rescan_ts: float = 0
        # Zenny detectado no último scan (usado para verificar se o struct ainda é válido)
        self._last_zenny: int = 0

    # --- Conexão ---

    def connect(self) -> bool:
        """Tenta conectar ao processo do MHW."""
        if not PYMEM_AVAILABLE:
            print("[MEMORY] [ERROR] Pymem nao esta instalado!")
            return False
        if not is_admin():
            print("[MEMORY] [WARNING] Nao esta rodando como Administrador! A leitura de memoria pode falhar.")
        try:
            with self._lock:
                self.pm = Pymem("MonsterHunterWorld.exe")
                self.base = self.pm.process_base.lpBaseOfDll
                self.connected = True
                print(f"[MEMORY] [OK] Conectado ao MHW! Base: {hex(self.base)}")
                return True
        except Exception as e:
            print(f"[MEMORY] [ERROR] Falha ao conectar: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Desconecta do processo."""
        with self._lock:
            if self.pm:
                try:
                    self.pm.close_process()
                except Exception:
                    pass
            self.pm = None
            self.connected = False
            self._cache = {}
            print("[MEMORY] ❌ Desconectado do MHW.")

    def is_connected(self) -> bool:
        """Verifica se ainda está conectado."""
        if not self.pm or not self.connected:
            return False
        try:
            # Tentar ler um byte da base para ver se o processo existe
            self.pm.read_bytes(self.base, 1)
            return True
        except Exception:
            self.connected = False
            self.player_struct_addr = 0
            return False

    # --- Leitura Segura ---

    def _read_ptr_chain(self, base_offset: int, offsets: List[int]) -> Optional[int]:
        """
        Segue uma cadeia de ponteiros: base + base_offset → [off0] → [off1] → ... → addr + offN
        Retorna o endereço final ou None se qualquer leitura falhar.
        """
        if self.pm is None or not self.connected:
            return None
        try:
            addr: int = self.pm.read_longlong(self.base + base_offset)
            if addr == 0:
                return None
            for i in range(len(offsets) - 1):
                addr = self.pm.read_longlong(addr + offsets[i])
                if addr == 0:
                    return None
            return addr + offsets[-1]
        except Exception:
            return None

    def _ri32(self, address: int) -> Optional[int]:
        """Lê int32 seguro."""
        if self.pm is None:
            return None
        try:
            return self.pm.read_int(address)
        except Exception:
            return None

    def _ri64(self, address: int) -> Optional[int]:
        """Lê int64 seguro."""
        if self.pm is None:
            return None
        try:
            return self.pm.read_longlong(address)
        except Exception:
            return None

    def _rf32(self, address: int) -> Optional[float]:
        """Lê float32 seguro."""
        if self.pm is None:
            return None
        try:
            return self.pm.read_float(address)
        except Exception:
            return None

    def _rstr(self, address: int, length: int = 64) -> Optional[str]:
        """Lê string UTF-8 segura."""
        if self.pm is None:
            return None
        try:
            raw = self.pm.read_bytes(address, length)
            # Tentar decodificar como UTF-8, lidando com caracteres especiais (ã, etc)
            return raw.split(b'\x00')[0].decode('utf-8', errors='ignore')
        except Exception:
            return None

    # --- Scanner de Memória Dinâmico ---

    def find_player_struct(self, force_rescan: bool = False) -> int:
        """Busca o struct de save na memória (usado para HR, MR, Zenny)."""
        now = time.time()
        
        # Se já temos um endereço, validar se ele ainda é o bloco do jogador
        if self.player_struct_addr and not force_rescan:
            try:
                # Verificação rápida (apenas 10 bytes) para ver se o nome ainda está lá
                name_bytes = self.pm.read_bytes(self.player_struct_addr, 10)
                if b"LittleJ" in name_bytes:
                    return self.player_struct_addr
                else:
                    self.player_struct_addr = 0
            except:
                self.player_struct_addr = 0

        # Throttle: evitar rescaneamento frenético se o jogo estiver fechando ou carregando
        if not force_rescan and (now - self._last_rescan_ts < 10):
            return 0

        if not self.pm:
            return 0

        self._last_rescan_ts = now
        print("[MEMORY] [SCAN] Iniciando Smart Scan (Seis Olhos) para sincronizar dados...")
        
        # Padrão de busca: "LittleJão" em UTF-8
        # LittleJão = 4c 69 74 74 6c 65 4a c3 a3 6f
        name_pattern = b"LittleJ\xc3\xa3o"
        
        # 1. Tentar ler do offset direto conhecido (SaveData region)
        hr_direct = self._ri32(self.base + self.DIRECT_HR_OFFSET)
        if hr_direct == 54:
            # HR bateu. O nome deve estar perto.
            # No MHW, o HR 54 e MR 10 ficam em blocos de struct.
            pass

        # 2. Varredura no heap (mais robusto)
        try:
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
                if k32.VirtualQueryEx(self.pm.process_handle, ctypes.c_ulonglong(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
                    break
                
                # Somente regiões commitadas e passíveis de leitura/escrita
                if mbi.State == 0x1000 and mbi.Protect in {0x02, 0x04, 0x20, 0x40}:
                    # Limitar scan a regiões razoáveis para evitar overhead
                    if 0 < mbi.RegionSize < 100 * 1024 * 1024:
                        try:
                            # Buscar assinatura
                            data = self.pm.read_bytes(mbi.BaseAddress, mbi.RegionSize)
                            idx = data.find(name_pattern)
                            while idx != -1:
                                potential_addr = mbi.BaseAddress + idx
                                # Validar HR (54) e MR (10) perto do nome
                                # Baseado nos achados do diagnostico: HR em +0x40, Zenny em +0x44, MR em +0x84
                                try:
                                    hr = struct.unpack('<I', data[idx+0x40 : idx+0x44])[0] if idx+0x44 < len(data) else 0
                                    zenny = struct.unpack('<I', data[idx+0x44 : idx+0x48])[0] if idx+0x48 < len(data) else 0
                                    mr = struct.unpack('<I', data[idx+0x84 : idx+0x88])[0] if idx+0x88 < len(data) else 0
                                    
                                    # Critérios de validação de um struct de PLAYER real:
                                    # 1. HR deve ser o esperado (54)
                                    # 2. MR deve ser razoável (1 a 999)
                                    # 3. Zenny deve ser razoável (>0 e < 100M)
                                    if hr == 54 and 0 < mr < 1000 and 0 < zenny < 100000000:
                                        print(f"[MEMORY] [SUCCESS] Struct REAL do jogador encontrado em {hex(potential_addr)} (HR={hr}, MR={mr}, Zenny={zenny})")
                                        self.player_struct_addr = potential_addr
                                        return potential_addr
                                except: pass
                                idx = data.find(name_pattern, idx + 1)
                        except: pass
                addr = mbi.BaseAddress + mbi.RegionSize
        except Exception as e:
            print(f"[MEMORY] [ERROR] Erro no Smart Scan: {e}")

        return 0

    # ============================================================
    # PLAYER INFO (HR, MR, Nome)
    # ============================================================
    
    # Offset direto do módulo (descoberto via memory scan)
    # HR está em base + 0x2F78D10, MR em base + 0x2F78D14
    DIRECT_HR_OFFSET = 0x2F78D10
    DIRECT_MR_OFFSET = 0x2F78D14
    
    def get_player_info(self) -> Dict[str, Any]:
        """Lê Nome, HR, MR e Zenny diretamente do Struct de Save calibrado."""
        result = {"name": "Desconhecido", "hr": 0, "mr": 0, "zenny": 0}
        
        struct_addr = self.find_player_struct()
        if struct_addr:
            try:
                # Nome em UTF-8 (até 16 chars)
                name_bytes = self.pm.read_bytes(struct_addr + STRUCT_OFFSETS["NAME"], 16)
                result["name"] = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
                
                # HR, MR e Zenny
                hr = self._ri32(struct_addr + STRUCT_OFFSETS["HR"])
                mr = self._ri32(struct_addr + STRUCT_OFFSETS["MR"])
                result["hr"] = hr if hr is not None else 0
                result["mr"] = mr if mr is not None else 0
                result["zenny"] = self._ri32(struct_addr + STRUCT_OFFSETS["ZENNY"]) or 0
                
                # Validação contra valores absurdos
                hr_val = int(result["hr"])
                mr_val = int(result["mr"])
                if hr_val > 999 or hr_val < 0: result["hr"] = 0
                if mr_val > 999 or mr_val < 0: result["mr"] = 0
                
            except Exception as e:
                print(f"[MEMORY] Erro ao ler player info no struct: {e}")
        
        return result

    # ============================================================
    # ARMA EQUIPADA
    # ============================================================
    DIRECT_WEAPON_ID_OFFSET = 0x2F185DC  # Offset direto do módulo (descoberto via memory scan)
    
    def get_weapon_info(self) -> Dict[str, Any]:
        """Lê tipo e ID escaneando o contexto do objeto de equipamento ativo."""
        result: Dict[str, Any] = {
            "type_id": None,
            "type": None,
            "id": None,
            "name": None,
            "sharpness": None,
        }

        try:
            # 1. Pegar o objeto base do jogador em combate/cidade
            # Esse ponteiro é a raiz para quase tudo que é 'ao vivo'
            player_ptr = self._read_ptr_chain(ADDRESSES["WEAPON"], [0x50, 0xC0, 0x8, 0x78])
            
            if player_ptr:
                # Vamos ler uma janela de 1024 bytes ao redor dos offsets de equipamento (0x280 - 0x350)
                # O ID e o Tipo costumam estar aqui, mas o offset exato muda entre cidade e missão.
                data = self.pm.read_bytes(player_ptr + 0x280, 200)
                
                # Procurar por um padrão válido: [ID (4 bytes)][Tipo (4 bytes)]
                # Onde Tipo está entre 0 e 13 e ID é > 0
                for i in range(0, len(data) - 8, 4):
                    wid = struct.unpack('<I', data[i:i+4])[0]
                    wtype = struct.unpack('<I', data[i+4:i+8])[0]
                    
                    if 0 <= wtype <= 13 and 100 < wid < 10000:
                        # Achamos um par ID/Tipo plausível!
                        result["id"] = wid
                        result["type_id"] = wtype
                        result["type"] = WEAPON_TYPES.get(wtype)
                        result["name"] = _lookup_name("weapon", wid)
                        break

            # 2. Fallback se o scan de contexto falhar
            if not result["id"]:
                struct_addr = self.find_player_struct()
                if struct_addr:
                    # No save: ID as vezes está em +0x78 e Tipo em +0x74
                    wid = self._ri32(struct_addr + 0x78)
                    wtype = self._ri32(struct_addr + 0x74)
                    if wtype is not None and 0 <= wtype <= 13 and wid and wid > 0:
                        result["id"] = wid
                        result["type_id"] = wtype
                        result["type"] = WEAPON_TYPES.get(wtype)
                        result["name"] = _lookup_name("weapon", wid)

            # 3. Afiação (Sempre do Objeto Vivo)
            sharp_addr = self._read_ptr_chain(ADDRESSES["WEAPON"], OFFSETS["WEAPON_SHARPNESS"])
            if sharp_addr:
                sharpness = []
                for i in range(7):
                    val = self._ri32(sharp_addr + (i * 4))
                    sharpness.append(val if val is not None else 0)
                if any(v > 0 for v in sharpness):
                    result["sharpness"] = sharpness

        except Exception as e:
            print(f"[MEMORY] Erro na detecção por scan de contexto: {e}")

        return result

    # ============================================================
    # EQUIPAMENTO (ARMADURA + AMULETO)
    # ============================================================
    def get_equipment_info(self) -> Dict[str, Any]:
        """Lê IDs das peças de armadura e amuleto equipados."""
        result: Dict[str, Any] = {
            "head_id": None,
            "chest_id": None,
            "arms_id": None,
            "waist_id": None,
            "legs_id": None,
            "charm_id": None,
        }

        equip_addr = self._read_ptr_chain(ADDRESSES["EQUIPMENT"], OFFSETS["EQUIPMENT"])
        if equip_addr:
            for slot_name, slot_offset in EQUIPMENT_SLOTS.items():
                item_id = self._ri32(equip_addr + slot_offset)
                if item_id is not None and item_id > 0:
                    result[f"{slot_name}_id"] = item_id

        return result

    # ============================================================
    # SKILLS ATIVAS
    # ============================================================
    def get_active_skills(self) -> List[Dict[str, Any]]:
        """Lê as skills ativas do equipamento (com validação de endereço)."""
        skills = []
        # Tentar ler skills via pointer chain
        # [0x50, 0x7D20, 0x10, 0x78] - Offset pode mudar dependendo da versao
        skill_base = self._read_ptr_chain(ADDRESSES["WEAPON"], [0x50, 0x7D20, 0x10, 0x78])
        
        # Validar se o endereço é razoável (evita ler lixo no heap)
        if skill_base and skill_base > 0x10000:
            try:
                # O jogo armazena skills como um array de bytes (um para cada ID de skill tree)
                # Vamos ler os primeiros 200 bytes para cobrir a maioria das skills
                data = self.pm.read_bytes(skill_base, 200)
                for i in range(len(data)):
                    level = data[i]
                    if 0 < level <= 7:  # Limite de nível realista em MHW
                        skills.append({"id": i, "level": level})
            except:
                pass
        return skills

    # Alias para compatibilidade
    def get_gear_skills(self) -> List[Dict[str, Any]]:
        return self.get_active_skills()

    # ============================================================
    # MONSTROS
    # ============================================================
    @staticmethod
    def _safe_round(value: Optional[float], digits: int) -> Optional[float]:
        """Round helper that handles None values for type safety."""
        if value is None:
            return None
        # Explicit rounding via multiplication avoids Pyre2 round() overload bug
        factor = 10 ** digits
        return int(value * factor + 0.5) / factor

    def _read_monster_at(self, address: int) -> Optional[Dict[str, Any]]:
        """Lê os dados de um monstro específico com validação de sanidade."""
        # Validar endereço básico
        if address < 0x10000: return None
        
        mid = self._ri32(address + MONSTER_STRUCT["id"])
        hp = self._rf32(address + MONSTER_STRUCT["hp"])
        max_hp = self._rf32(address + MONSTER_STRUCT["max_hp"])
        crown_size = self._rf32(address + MONSTER_STRUCT["size"])

        if hp is None or max_hp is None:
            return None
            
        # Validação de HP range realista (proteção contra lixo de memória)
        hp_f = float(hp)
        max_hp_f = float(max_hp)
        
        if hp_f < 0 or hp_f > max_hp_f:
            return None

        hp_pct = self._safe_round((hp_f / max_hp_f) * 100, 1)
        
        return {
            "id": mid,
            "hp": self._safe_round(hp, 1),
            "max_hp": self._safe_round(max_hp, 1),
            "hp_percentage": hp_pct,
            "crown_size": self._safe_round(crown_size, 2),
        }

    def get_monsters(self) -> List[Dict[str, Any]]:
        """Lê dados dos monstros da quest atual (até 3)."""
        monsters: List[Dict[str, Any]] = []

        monster_base = self._read_ptr_chain(ADDRESSES["MONSTER"], OFFSETS["MONSTER"])
        if not monster_base:
            return monsters

        # Ler até 3 monstros seguindo a lista ligada
        addrs: List[int] = [monster_base]
        # Collect monster addresses by following the linked list
        for _ in range(2):
            last = addrs[-1]
            next_ptr = self._ri64(last + MONSTER_STRUCT["next"])
            if next_ptr is not None and next_ptr != last and next_ptr != 0:
                addrs.append(next_ptr)
            else:
                break

        for a in addrs:
            monster = self._read_monster_at(a)
            if monster is not None:
                monsters.append(monster)

        return monsters

    # ============================================================
    # ABNORMALITIES (BUFFS / DEBUFFS)
    # ============================================================
    def get_abnormalities(self) -> Dict[str, List[Dict[str, Any]]]:
        """Lê buffs e debuffs ativos."""
        result: Dict[str, List[Dict[str, Any]]] = {
            "consumable_buffs": [],
            "gear_buffs": [],
        }

        # Buffs de consumíveis
        abn_addr = self._read_ptr_chain(ADDRESSES["ABNORMALITY"], OFFSETS["ABNORMALITY"])
        if abn_addr:
            for name, offset in CONSUMABLE_BUFF_OFFSETS.items():
                timer = self._rf32(abn_addr + offset)
                if timer is not None and timer > 0:
                    timer_val: float = timer
                    result["consumable_buffs"].append({
                        "name": name,
                        "timer": int(timer_val * 10 + 0.5) / 10,
                    })

        # Buffs baseados em gear (mantos, etc.)
        gear_addr = self._read_ptr_chain(ADDRESSES["ABNORMALITY"], OFFSETS["ABNORMALITY_GEAR"])
        if gear_addr:
            mantle_checks = {
                "Manto Temporal": 0x0,
                "Manto de Rocha-firme": 0x10,
                "Manto de Evasão": 0x20,
                "Manto de Vitória": 0x30,
                "Manto de Gelo": 0x40,
            }
            for name, offset in mantle_checks.items():
                timer = self._rf32(gear_addr + offset)
                if timer is not None and timer > 0:
                    timer_val2: float = timer
                    cooldown = self._rf32(gear_addr + offset + 0x4)
                    result["gear_buffs"].append({
                        "name": name,
                        "timer": int(timer_val2 * 10 + 0.5) / 10,
                        "cooldown": self._safe_round(cooldown, 1),
                    })

        return result

    # ============================================================
    # DANO DO GRUPO (PARTY DAMAGE)
    # ============================================================
    def get_party_damage(self) -> List[Dict[str, Any]]:
        """Lê o dano de cada membro do grupo (até 4 jogadores)."""
        players: List[Dict[str, Any]] = []

        damage_addr = self._read_ptr_chain(ADDRESSES["DAMAGE"], OFFSETS["DAMAGE"])
        if not damage_addr:
            return players

        for i in range(4):
            player_base = damage_addr + (i * DAMAGE_PLAYER_STRIDE)
            name = self._rstr(player_base + DAMAGE_NAME_OFFSET, 48)
            damage = self._ri32(player_base + DAMAGE_VALUE_OFFSET)

            if name and len(name.strip()) > 0 and damage is not None and damage >= 0:
                players.append({
                    "index": i,
                    "name": name.strip(),
                    "damage": damage,
                    "percentage": 0.0,
                })

        # Calcular percentuais
        total = sum(p["damage"] for p in players) if players else 0
        for p in players:
            p["percentage"] = round((p["damage"] / total) * 100, 1) if total > 0 else 0.0

        return players

    # ============================================================
    # ZONA / QUEST
    # ============================================================
    def get_zone_info(self) -> Dict[str, Any]:
        """Lê zona atual e timer da quest."""
        result: Dict[str, Any] = {"zone_id": None, "quest_timer": None, "quest_timer_formatted": None}

        zone_addr = self._read_ptr_chain(ADDRESSES["ZONE"], OFFSETS["ZONE"])
        if zone_addr:
            result["zone_id"] = self._ri32(zone_addr)

        qt_addr = self._read_ptr_chain(ADDRESSES["QUEST_DATA"], OFFSETS["QUEST_TIMER"])
        if qt_addr:
            timer = self._rf32(qt_addr)
            if timer is not None and timer > 0:
                timer_val3: float = timer
                result["quest_timer"] = int(timer_val3 * 10 + 0.5) / 10
                mins = int(timer // 60)
                secs = int(timer % 60)
                result["quest_timer_formatted"] = f"{mins}:{secs:02d}"

        return result

    # ============================================================
    # SNAPSHOT COMPLETO
    # ============================================================
    def _build_snapshot(self) -> Dict[str, Any]:
        """Constrói um snapshot completo lendo todos os dados da memória."""
        now = time.time()
        return {
            "connected": True,
            "timestamp": int(now * 1000),
            "player": self.get_player_info(),
            "weapon": self.get_weapon_info(),
            "equipment": self.get_equipment_info(),
            "skills": self.get_gear_skills(),
            "monsters": self.get_monsters(),
            "abnormalities": self.get_abnormalities(),
            "party_damage": self.get_party_damage(),
            "zone": self.get_zone_info(),
        }

    def get_full_snapshot(self) -> Dict[str, Any]:
        """Retorna um snapshot completo (com cache de 500ms)."""
        now = time.time()

        if now - self._cache_ts < self._cache_ttl and self._cache:
            return self._cache

        if not self.connected:
            if not self.connect():
                return {"connected": False, "error": "MHW não encontrado. Certifique-se de que o jogo está aberto."}

        # Verificar se o processo ainda está vivo
        if not self.is_connected():
            return {"connected": False, "error": "Processo do MHW encerrado."}

        try:
            snapshot = self._build_snapshot()
            self._cache = snapshot
            self._cache_ts = now
            return snapshot

        except Exception as e:
            self.connected = False
            return {"connected": False, "error": str(e)}

    def get_fresh_snapshot(self) -> Dict[str, Any]:
        """
        Retorna um snapshot FRESCO, ignorando o cache.
        Usa para garantir dados em tempo real (ex: troca de arma no caixa).
        Também tenta auto-conectar se não estiver conectado.
        """
        # Auto-connect
        if not self.connected:
            if not self.connect():
                return {"connected": False, "error": "MHW não encontrado. Certifique-se de que o jogo está aberto."}

        # Verificar se o processo ainda está vivo
        if not self.is_connected():
            # Tentar reconectar uma vez
            self.connected = False
            if not self.connect():
                return {"connected": False, "error": "Processo do MHW encerrado. Tentativa de reconexão falhou."}

        try:
            snapshot = self._build_snapshot()
            # Atualizar cache também
            self._cache = snapshot
            self._cache_ts = time.time()
            return snapshot

        except Exception as e:
            self.connected = False
            return {"connected": False, "error": str(e)}


# ============================================================
# SINGLETON
# ============================================================
_reader: Optional[MHWMemoryReader] = None


def get_reader() -> MHWMemoryReader:
    """Retorna a instância global do leitor de memória."""
    global _reader
    if _reader is None:
        _reader = MHWMemoryReader()
    return _reader


# ============================================================
# TRADUÇÃO DE IDs → NOMES (usando mhw.db)
# ============================================================
# Cache para buscas no banco (evita abrir o arquivo mhw.db milhares de vezes)
_NAME_CACHE: Dict[str, str] = {}


def _get_db_path() -> str:
    """Retorna o caminho do banco de dados do jogo."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "mhw.db")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "mhw.db")


def _lookup_name(table: str, item_id: int) -> str:
    """Busca o nome (PT preferencial) de um item pelo ID."""
    cache_key = f"{table}:{item_id}"
    if cache_key in _NAME_CACHE:
        return _NAME_CACHE[cache_key]

    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.cursor()
        
        # Tabelas de texto costumam ser {table}_text
        text_table = f"{table}_text"
        cur.execute(f"SELECT name FROM {text_table} WHERE id = ? AND lang_id = 'pt' LIMIT 1", (item_id,))
        row = cur.fetchone()
        
        if not row:
            # Tentar em inglês se não houver em PT
            cur.execute(f"SELECT name FROM {text_table} WHERE id = ? AND lang_id = 'en' LIMIT 1", (item_id,))
            row = cur.fetchone()

        name = row[0] if row else f"Item {item_id}"
        _NAME_CACHE[cache_key] = name
        conn.close()
        return name
    except:
        return f"Item {item_id}"


def _lookup_skill_name(skill_id: int) -> str:
    """Busca o nome da skill pelo skilltree_id."""
    cache_key = f"skill:{skill_id}"
    if cache_key in _NAME_CACHE:
        return _NAME_CACHE[cache_key]

    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.cursor()
        cur.execute("SELECT name FROM skilltree_text WHERE id = ? AND lang_id = 'pt' LIMIT 1", (skill_id,))
        row = cur.fetchone()
        
        if not row:
            cur.execute("SELECT name FROM skilltree_text WHERE id = ? AND lang_id = 'en' LIMIT 1", (skill_id,))
            row = cur.fetchone()

        name = row[0] if row else f"Skill {skill_id}"
        _NAME_CACHE[cache_key] = name
        conn.close()
        return name
    except:
        return f"Skill {skill_id}"


def _lookup_monster_name(monster_id: int) -> str:
    """Busca o nome do monstro pelo ID."""
    return _lookup_name("monster", monster_id)


# ============================================================
# CONTEXTO PARA A IA
# ============================================================
def get_player_context_for_ai() -> str:
    """
    Gera uma string legível com o estado REAL do jogador.
    Essa string é injetada no system prompt para eliminar alucinações.
    Traduz IDs para nomes usando o banco de dados local.
    
    IMPORTANTE: Usa get_fresh_snapshot() para SEMPRE ler dados frescos
    da memória (ignora cache). Assim troca de arma, equipamento, etc.
    são detectados em tempo real a cada mensagem do chat.
    """
    reader = get_reader()
    # Forçar leitura fresca (sem cache) para detectar mudanças em tempo real
    snapshot = reader.get_fresh_snapshot()

    if not snapshot.get("connected"):
        print("[MEMORY] ⚠️ Não conectado ao MHW — contexto de memória vazio.")
        return ""

    print("[MEMORY] ✅ Leitura em tempo real — gerando contexto para a IA...")

    lines = ["", "═══ DADOS EM TEMPO REAL (LEITURA DE MEMÓRIA DO JOGO) ═══"]

    # --- Player ---
    player = snapshot.get("player", {})
    if player.get("name"):
        lines.append(f"Ca\u00e7ador: {player['name']}")
    if player.get("mr") is not None:
        lines.append(f"Master Rank (MR): {player['mr']}")
    if player.get("hr") is not None:
        lines.append(f"Hunter Rank (HR): {player['hr']}")
    if player.get("zenny") is not None:
        lines.append(f"Zenny: {player['zenny']:,}z")

    # --- Weapon ---
    weapon = snapshot.get("weapon", {})
    if weapon.get("type"):
        wname = weapon.get("name", "Desconhecida")
        wid = weapon.get("id")
        lines.append(f"\n🗡️ Arma Equipada: {wname} ({weapon['type']})")
        if wid:
            lines.append(f"   ID no Banco: {wid}")
    if weapon.get("sharpness"):
        sharp_parts = [f"{c}: {v}" for c, v in zip(SHARPNESS_COLORS, weapon['sharpness']) if v > 0]
        lines.append(f"   Afiação: {', '.join(sharp_parts)}")

    # --- Equipment ---
    equip = snapshot.get("equipment", {})
    slot_labels = {
        "head_id": "🪖 Elmo", "chest_id": "🦺 Torso", "arms_id": "🧤 Braços",
        "waist_id": "🩲 Cinturão", "legs_id": "🥾 Grevas", "charm_id": "📿 Amuleto",
    }
    equip_parts = []
    for key, label in slot_labels.items():
        eid = equip.get(key)
        if eid is not None and eid > 0:
            table = "charm" if "charm" in key else "armor"
            ename = _lookup_name(table, eid)
            equip_parts.append(f"{label}: {ename}")
    if equip_parts:
        lines.append("\n🛡️ Equipamento Atual:")
        for part in equip_parts:
            lines.append(f"   {part}")

    # --- Skills ---
    skills = snapshot.get("skills", [])
    if skills:
        lines.append(f"\n⚡ Skills Ativas ({len(skills)}):")
        for s in skills[:25]:
            sname = _lookup_skill_name(s['id'])
            lines.append(f"   • {sname}: Nível {s['level']}")

    # --- Monsters ---
    monsters = snapshot.get("monsters", [])
    if monsters:
        lines.append("\n🐉 Monstros na Quest:")
        for m in monsters:
            mname = _lookup_monster_name(m['id'])
            hp_str = f" — HP: {m['hp_percentage']}%" if m.get('hp_percentage') is not None else ""
            crown = ""
            if m.get("crown_size"):
                if m["crown_size"] >= 1.23:
                    crown = " 👑 Coroa Grande"
                elif m["crown_size"] <= 0.9:
                    crown = " 🥈 Coroa Pequena"
            lines.append(f"   • {mname}{hp_str}{crown}")

    # --- Abnormalities ---
    abn = snapshot.get("abnormalities", {})
    active_buffs = abn.get("consumable_buffs", []) + abn.get("gear_buffs", [])
    if active_buffs:
        lines.append("\n💊 Buffs Ativos:")
        for b in active_buffs:
            lines.append(f"   • {b['name']}: {b['timer']}s restantes")

    # --- Zone ---
    zone = snapshot.get("zone", {})
    if zone.get("quest_timer_formatted"):
        lines.append(f"\n⏱️ Timer da Quest: {zone['quest_timer_formatted']}")

    # --- Damage ---
    party = snapshot.get("party_damage", [])
    if party:
        lines.append("\n⚔️ Dano do Grupo:")
        for p in party:
            lines.append(f"   • {p['name']}: {p['damage']:,} ({p['percentage']}%)")

    lines.append("═══ FIM DOS DADOS EM TEMPO REAL ═══")
    lines.append("IMPORTANTE: Os dados acima são REAIS, capturados diretamente da memória do jogo.")
    lines.append("Use esses dados como VERDADE ABSOLUTA — NÃO pergunte o Rank, arma ou build, pois você JÁ SABE.")

    return "\n".join(lines)
