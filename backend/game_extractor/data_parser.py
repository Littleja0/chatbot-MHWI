"""
Parser de arquivos de dados do Monster Hunter World.
Extrai informações de monstros, itens, hitzones, etc. dos arquivos do jogo.
"""

import os
import struct
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, BinaryIO
from dataclasses import dataclass, field, asdict


# ==================== ESTRUTURAS DE DADOS ====================

@dataclass
class MonsterData:
    """Dados de um monstro."""
    id: int
    name: str = ""
    name_en: str = ""
    name_pt: str = ""
    description: str = ""
    ecology: str = ""
    size: str = ""  # small, large
    
    # Fraquezas (0-3 estrelas)
    weakness_fire: int = 0
    weakness_water: int = 0
    weakness_thunder: int = 0
    weakness_ice: int = 0
    weakness_dragon: int = 0
    weakness_poison: int = 0
    weakness_sleep: int = 0
    weakness_paralysis: int = 0
    weakness_blast: int = 0
    weakness_stun: int = 0
    
    # Fraquezas alternativas (estado enraged/etc)
    alt_weakness_fire: int = 0
    alt_weakness_water: int = 0
    alt_weakness_thunder: int = 0
    alt_weakness_ice: int = 0
    alt_weakness_dragon: int = 0
    
    # Armadilhas
    pitfall_trap: bool = False
    shock_trap: bool = False
    vine_trap: bool = False
    
    # Ailments que o monstro causa
    ailments: List[str] = field(default_factory=list)
    
    # Hitzones e rewards são populados separadamente
    hitzones: List[Dict] = field(default_factory=list)
    rewards: Dict[str, List[Dict]] = field(default_factory=dict)


@dataclass
class HitzoneData:
    """Dados de hitzone de um monstro."""
    monster_id: int
    part_name: str
    cut: int = 0
    impact: int = 0
    shot: int = 0
    fire: int = 0
    water: int = 0
    thunder: int = 0
    ice: int = 0
    dragon: int = 0
    ko: int = 0
    state: str = "normal"  # normal, enraged, broken


@dataclass
class ItemData:
    """Dados de um item."""
    id: int
    name: str = ""
    name_en: str = ""
    name_pt: str = ""
    description: str = ""
    rarity: int = 1
    category: str = ""
    buy_price: int = 0
    sell_price: int = 0
    carry_limit: int = 0


@dataclass
class RewardData:
    """Dados de recompensa/drop de um monstro."""
    monster_id: int
    item_id: int
    item_name: str = ""
    rank: str = ""  # LR, HR, MR
    condition: str = ""  # Carve, Capture, Break, etc
    stack: int = 1
    percentage: float = 0.0


# ==================== PARSERS DE ARQUIVO ====================

class GMDParser:
    """
    Parser de arquivos GMD (Game Message Data).
    Contém textos localizados do jogo.
    """
    
    # Mapeamento de códigos de idioma
    LANG_CODES = {
        0: "ja",    # Japonês
        1: "en",    # Inglês
        2: "fr",    # Francês
        3: "it",    # Italiano
        4: "de",    # Alemão
        5: "es",    # Espanhol
        6: "pt",    # Português
        7: "pl",    # Polonês
        8: "ru",    # Russo
        9: "ko",    # Coreano
        10: "zh_tw", # Chinês tradicional
        11: "zh_cn", # Chinês simplificado
        12: "ar",   # Árabe
    }
    
    def __init__(self):
        self.entries = {}
    
    def parse(self, data: bytes) -> Dict[str, str]:
        """
        Parse um arquivo GMD e retorna dict de chave -> texto.
        """
        if len(data) < 32:
            return {}
        
        # Verificar magic
        magic = data[:4]
        if magic != b'GMD\x00':
            return {}
        
        try:
            # Header
            version = struct.unpack_from('<I', data, 4)[0]
            
            if version == 0x00010302:  # MHW format
                return self._parse_mhw_gmd(data)
            else:
                # Tentar formato genérico
                return self._parse_generic_gmd(data)
                
        except Exception as e:
            print(f"Erro ao parsear GMD: {e}")
            return {}
    
    def _parse_mhw_gmd(self, data: bytes) -> Dict[str, str]:
        """Parse formato GMD do MHW."""
        entries = {}
        
        try:
            # Estrutura do header MHW GMD:
            # 0x00: Magic "GMD\x00"
            # 0x04: Version
            # 0x08: Language ID
            # 0x0C: ???
            # 0x10: Key count
            # 0x14: String count
            # 0x18: Key block size
            # 0x1C: String block size
            # 0x20: Name (32 bytes)
            # 0x40: Keys
            # Keys + Key block size: Strings
            
            lang_id = struct.unpack_from('<I', data, 0x08)[0]
            key_count = struct.unpack_from('<I', data, 0x10)[0]
            string_count = struct.unpack_from('<I', data, 0x14)[0]
            key_block_size = struct.unpack_from('<I', data, 0x18)[0]
            string_block_size = struct.unpack_from('<I', data, 0x1C)[0]
            
            # Nome do arquivo interno
            name_bytes = data[0x20:0x40]
            name_end = name_bytes.find(b'\x00')
            internal_name = name_bytes[:name_end].decode('utf-8', errors='ignore') if name_end > 0 else ""
            
            # Offset onde começam as chaves
            keys_offset = 0x40
            
            # Parsear chaves (cada entrada tem 8 bytes: offset + hash)
            keys = []
            for i in range(key_count):
                entry_offset = keys_offset + (i * 8)
                if entry_offset + 8 > len(data):
                    break
                    
                key_offset = struct.unpack_from('<I', data, entry_offset)[0]
                key_hash = struct.unpack_from('<I', data, entry_offset + 4)[0]
                keys.append((key_offset, key_hash))
            
            # Offset onde começam as strings
            strings_offset = keys_offset + key_block_size
            
            # Parsear strings
            current_pos = strings_offset
            string_idx = 0
            
            while current_pos < len(data) and string_idx < string_count:
                # Encontrar fim da string (null terminator)
                end_pos = data.find(b'\x00', current_pos)
                if end_pos == -1:
                    break
                
                string_data = data[current_pos:end_pos]
                try:
                    text = string_data.decode('utf-8')
                except:
                    text = string_data.decode('latin-1', errors='ignore')
                
                # Usar índice como chave se não tivermos a chave real
                key = f"string_{string_idx}"
                if string_idx < len(keys):
                    key = f"key_{keys[string_idx][1]:08x}"
                
                entries[key] = text
                
                current_pos = end_pos + 1
                string_idx += 1
            
            # Adicionar metadados
            entries['_lang_id'] = self.LANG_CODES.get(lang_id, f"unk_{lang_id}")
            entries['_name'] = internal_name
            
        except Exception as e:
            print(f"Erro no parse MHW GMD: {e}")
        
        return entries
    
    def _parse_generic_gmd(self, data: bytes) -> Dict[str, str]:
        """Parse formato GMD genérico."""
        entries = {}
        # Implementação simplificada
        return entries


class MonsterDataParser:
    """
    Parser de dados de monstros do MHW.
    Arquivos: em/emXXX/*.dtt_rsz, *.em_rsz
    """
    
    # Mapeamento de IDs de monstro para nomes (base game)
    MONSTER_IDS = {
        1: "Rathian",
        2: "Rathalos",
        3: "Diablos",
        4: "Kirin",
        5: "Kushala Daora",
        6: "Teostra",
        7: "Lunastra",
        8: "Nergigante",
        9: "Vaal Hazak",
        10: "Xeno'jiiva",
        11: "Zorah Magdaros",
        12: "Anjanath",
        13: "Barroth",
        14: "Bazelgeuse",
        15: "Behemoth",
        16: "Deviljho",
        17: "Dodogama",
        18: "Great Girros",
        19: "Great Jagras",
        20: "Jyuratodus",
        21: "Kulu-Ya-Ku",
        22: "Kulve Taroth",
        23: "Lavasioth",
        24: "Legiana",
        25: "Leshen",
        26: "Odogaron",
        27: "Paolumu",
        28: "Pink Rathian",
        29: "Pukei-Pukei",
        30: "Radobaan",
        31: "Tobi-Kadachi",
        32: "Tzitzi-Ya-Ku",
        33: "Uragaan",
        34: "Azure Rathalos",
        35: "Black Diablos",
        # Iceborne
        100: "Banbaro",
        101: "Barioth",
        102: "Beotodus",
        103: "Brachydios",
        104: "Glavenus",
        105: "Nargacuga",
        106: "Tigrex",
        107: "Velkhana",
        108: "Namielle",
        109: "Shara Ishvalda",
        110: "Zinogre",
        111: "Alatreon",
        112: "Fatalis",
        113: "Safi'jiiva",
        # ... mais podem ser adicionados
    }
    
    def __init__(self, extracted_path: Path):
        self.extracted_path = extracted_path
        self.monsters: Dict[int, MonsterData] = {}
    
    def parse_all(self) -> Dict[int, MonsterData]:
        """
        Parseia todos os dados de monstros encontrados.
        """
        em_folder = self.extracted_path / "em"
        if not em_folder.exists():
            em_folder = self.extracted_path / "merged" / "em"
        
        if not em_folder.exists():
            print(f"Pasta de monstros não encontrada: {em_folder}")
            return {}
        
        # Iterar sobre pastas de monstros (em001, em002, etc.)
        for monster_folder in em_folder.iterdir():
            if not monster_folder.is_dir():
                continue
            
            # Extrair ID do monstro do nome da pasta
            folder_name = monster_folder.name
            if folder_name.startswith("em"):
                try:
                    monster_id = int(folder_name[2:5])
                    monster_data = self._parse_monster_folder(monster_folder, monster_id)
                    if monster_data:
                        self.monsters[monster_id] = monster_data
                except ValueError:
                    continue
        
        return self.monsters
    
    def _parse_monster_folder(self, folder: Path, monster_id: int) -> Optional[MonsterData]:
        """
        Parseia a pasta de um monstro.
        """
        monster = MonsterData(
            id=monster_id,
            name_en=self.MONSTER_IDS.get(monster_id, f"Monster {monster_id}")
        )
        
        # Procurar arquivos de dados
        for file in folder.rglob("*"):
            if file.suffix in ['.dtt_rsz', '.em_rsz']:
                self._parse_monster_rsz(file, monster)
            elif file.suffix == '.gmd':
                self._parse_monster_gmd(file, monster)
        
        return monster if monster.name_en else None
    
    def _parse_monster_rsz(self, file: Path, monster: MonsterData):
        """
        Parseia arquivo RSZ com dados do monstro.
        """
        try:
            with open(file, 'rb') as f:
                data = f.read()
            
            # O formato RSZ é complexo e varia
            # Esta é uma implementação simplificada
            
            # Procurar por padrões conhecidos de dados de hitzone
            # (os valores geralmente estão em sequência)
            
        except Exception as e:
            print(f"Erro ao parsear {file.name}: {e}")
    
    def _parse_monster_gmd(self, file: Path, monster: MonsterData):
        """
        Parseia arquivo GMD com textos do monstro.
        """
        try:
            with open(file, 'rb') as f:
                data = f.read()
            
            parser = GMDParser()
            texts = parser.parse(data)
            
            # Atribuir textos ao monstro
            lang = texts.get('_lang_id', 'en')
            
            for key, value in texts.items():
                if key.startswith('_'):
                    continue
                
                # O primeiro texto geralmente é o nome
                if not monster.name:
                    monster.name = value
                    if lang == 'en':
                        monster.name_en = value
                    elif lang == 'pt':
                        monster.name_pt = value
                
        except Exception as e:
            print(f"Erro ao parsear GMD {file.name}: {e}")


class HitzoneParser:
    """
    Parser de hitzones do monstro.
    Os dados de hitzone estão geralmente em arquivos .dtt_rsz ou tabelas específicas.
    """
    
    def __init__(self, extracted_path: Path):
        self.extracted_path = extracted_path
    
    def parse_hitzones(self, monster_id: int) -> List[HitzoneData]:
        """
        Extrai dados de hitzone para um monstro específico.
        """
        hitzones = []
        
        # Procurar na pasta do monstro
        em_folder = self.extracted_path / "em" / f"em{monster_id:03d}"
        if not em_folder.exists():
            em_folder = self.extracted_path / "merged" / "em" / f"em{monster_id:03d}"
        
        if not em_folder.exists():
            return hitzones
        
        # Procurar arquivos de hitzone
        for file in em_folder.rglob("*.dtt_rsz"):
            parsed = self._parse_hitzone_file(file, monster_id)
            hitzones.extend(parsed)
        
        return hitzones
    
    def _parse_hitzone_file(self, file: Path, monster_id: int) -> List[HitzoneData]:
        """
        Parseia um arquivo de hitzone.
        """
        hitzones = []
        
        try:
            with open(file, 'rb') as f:
                data = f.read()
            
            # Procurar padrões de dados de hitzone
            # Formato típico: sequência de valores de dano por parte
            # [cut, impact, shot, fire, water, thunder, ice, dragon, ko]
            
            # Esta é uma heurística - o formato real é mais complexo
            
        except Exception as e:
            print(f"Erro ao parsear hitzone {file.name}: {e}")
        
        return hitzones


class ItemParser:
    """
    Parser de dados de itens.
    """
    
    def __init__(self, extracted_path: Path):
        self.extracted_path = extracted_path
        self.items: Dict[int, ItemData] = {}
    
    def parse_all(self) -> Dict[int, ItemData]:
        """
        Parseia todos os dados de itens.
        """
        item_folder = self.extracted_path / "common" / "item"
        if not item_folder.exists():
            item_folder = self.extracted_path / "merged" / "common" / "item"
        
        if not item_folder.exists():
            return {}
        
        # Procurar arquivos de item
        for file in item_folder.rglob("*.itm"):
            self._parse_item_file(file)
        
        # Procurar textos de item (GMD)
        text_folder = self.extracted_path / "common" / "text"
        if not text_folder.exists():
            text_folder = self.extracted_path / "merged" / "common" / "text"
        
        if text_folder.exists():
            for file in text_folder.rglob("*item*.gmd"):
                self._parse_item_texts(file)
        
        return self.items
    
    def _parse_item_file(self, file: Path):
        """Parse arquivo de item binário."""
        try:
            with open(file, 'rb') as f:
                data = f.read()
            
            # Formato simplificado - o real é mais complexo
            
        except Exception as e:
            print(f"Erro ao parsear item {file.name}: {e}")
    
    def _parse_item_texts(self, file: Path):
        """Parse textos de itens do GMD."""
        try:
            with open(file, 'rb') as f:
                data = f.read()
            
            parser = GMDParser()
            texts = parser.parse(data)
            
            # Associar textos aos itens
            
        except Exception as e:
            print(f"Erro ao parsear item GMD {file.name}: {e}")


# ==================== FUNÇÃO PRINCIPAL ====================

def parse_game_data(extracted_path: str) -> Dict[str, Any]:
    """
    Função principal para parsear todos os dados do jogo.
    
    Args:
        extracted_path: Caminho para os arquivos extraídos
    
    Returns:
        Dict com todos os dados parseados
    """
    extracted = Path(extracted_path)
    
    print("Parseando dados do jogo...")
    
    # Parsear monstros
    print("  - Monstros...")
    monster_parser = MonsterDataParser(extracted)
    monsters = monster_parser.parse_all()
    print(f"    {len(monsters)} monstros encontrados")
    
    # Parsear itens
    print("  - Itens...")
    item_parser = ItemParser(extracted)
    items = item_parser.parse_all()
    print(f"    {len(items)} itens encontrados")
    
    # Combinar dados
    result = {
        "monsters": {mid: asdict(m) for mid, m in monsters.items()},
        "items": {iid: asdict(i) for iid, i in items.items()},
        "version": "extracted",
        "source": str(extracted)
    }
    
    # Salvar JSON intermediário
    output_file = extracted / "parsed_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nDados salvos em: {output_file}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = str(Path(__file__).parent / "extracted_data")
    
    result = parse_game_data(path)
    print(f"\nTotal: {len(result['monsters'])} monstros, {len(result['items'])} itens")
