"""
Gerador de banco de dados SQLite a partir dos dados extraídos do jogo.
Cria um banco compatível com o formato usado pelo MHWorldData.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


# Schema do banco de dados (compatível com MHWorldData)
SCHEMA = """
-- Tabela de idiomas
CREATE TABLE IF NOT EXISTS language (
    id TEXT PRIMARY KEY,
    name TEXT,
    is_complete INTEGER DEFAULT 0
);

-- Tabela de monstros
CREATE TABLE IF NOT EXISTS monster (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    size TEXT,
    icon TEXT,
    pitfall_trap INTEGER DEFAULT 0,
    shock_trap INTEGER DEFAULT 0,
    vine_trap INTEGER DEFAULT 0,
    has_weakness INTEGER DEFAULT 1,
    has_alt_weakness INTEGER DEFAULT 0,
    weakness_fire INTEGER DEFAULT 0,
    weakness_water INTEGER DEFAULT 0,
    weakness_ice INTEGER DEFAULT 0,
    weakness_thunder INTEGER DEFAULT 0,
    weakness_dragon INTEGER DEFAULT 0,
    weakness_poison INTEGER DEFAULT 0,
    weakness_sleep INTEGER DEFAULT 0,
    weakness_paralysis INTEGER DEFAULT 0,
    weakness_blast INTEGER DEFAULT 0,
    weakness_stun INTEGER DEFAULT 0,
    alt_weakness_fire INTEGER DEFAULT 0,
    alt_weakness_water INTEGER DEFAULT 0,
    alt_weakness_ice INTEGER DEFAULT 0,
    alt_weakness_thunder INTEGER DEFAULT 0,
    alt_weakness_dragon INTEGER DEFAULT 0,
    alt_weakness_poison INTEGER DEFAULT 0,
    alt_weakness_sleep INTEGER DEFAULT 0,
    alt_weakness_paralysis INTEGER DEFAULT 0,
    alt_weakness_blast INTEGER DEFAULT 0,
    alt_weakness_stun INTEGER DEFAULT 0,
    ailment_roar TEXT,
    ailment_wind TEXT,
    ailment_tremor TEXT,
    ailment_defensedown INTEGER DEFAULT 0,
    ailment_fireblight INTEGER DEFAULT 0,
    ailment_waterblight INTEGER DEFAULT 0,
    ailment_thunderblight INTEGER DEFAULT 0,
    ailment_iceblight INTEGER DEFAULT 0,
    ailment_dragonblight INTEGER DEFAULT 0,
    ailment_blastblight INTEGER DEFAULT 0,
    ailment_regional INTEGER DEFAULT 0,
    ailment_poison INTEGER DEFAULT 0,
    ailment_sleep INTEGER DEFAULT 0,
    ailment_paralysis INTEGER DEFAULT 0,
    ailment_bleed INTEGER DEFAULT 0,
    ailment_stun INTEGER DEFAULT 0,
    ailment_mud INTEGER DEFAULT 0,
    ailment_effluvia INTEGER DEFAULT 0
);

-- Textos de monstros (localizados)
CREATE TABLE IF NOT EXISTS monster_text (
    id INTEGER,
    lang_id TEXT,
    name TEXT,
    ecology TEXT,
    description TEXT,
    alt_state_description TEXT,
    PRIMARY KEY (id, lang_id),
    FOREIGN KEY (id) REFERENCES monster(id)
);

-- Hitzones de monstros
CREATE TABLE IF NOT EXISTS monster_hitzone (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id INTEGER,
    cut INTEGER DEFAULT 0,
    impact INTEGER DEFAULT 0,
    shot INTEGER DEFAULT 0,
    fire INTEGER DEFAULT 0,
    water INTEGER DEFAULT 0,
    ice INTEGER DEFAULT 0,
    thunder INTEGER DEFAULT 0,
    dragon INTEGER DEFAULT 0,
    ko INTEGER DEFAULT 0,
    FOREIGN KEY (monster_id) REFERENCES monster(id)
);

-- Textos de hitzones (partes do corpo)
CREATE TABLE IF NOT EXISTS monster_hitzone_text (
    id INTEGER,
    lang_id TEXT,
    name TEXT,
    PRIMARY KEY (id, lang_id),
    FOREIGN KEY (id) REFERENCES monster_hitzone(id)
);

-- Recompensas de monstros
CREATE TABLE IF NOT EXISTS monster_reward (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monster_id INTEGER,
    condition_id INTEGER,
    rank TEXT,
    item_id INTEGER,
    stack INTEGER DEFAULT 1,
    percentage INTEGER DEFAULT 0,
    FOREIGN KEY (monster_id) REFERENCES monster(id),
    FOREIGN KEY (item_id) REFERENCES item(id)
);

-- Condições de recompensa
CREATE TABLE IF NOT EXISTS monster_reward_condition_text (
    id INTEGER,
    lang_id TEXT,
    name TEXT,
    PRIMARY KEY (id, lang_id)
);

-- Tabela de itens
CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY,
    category TEXT,
    subcategory TEXT,
    rarity INTEGER DEFAULT 1,
    buy_price INTEGER DEFAULT 0,
    sell_price INTEGER DEFAULT 0,
    carry_limit INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    icon_name TEXT,
    icon_color TEXT
);

-- Textos de itens
CREATE TABLE IF NOT EXISTS item_text (
    id INTEGER,
    lang_id TEXT,
    name TEXT,
    description TEXT,
    PRIMARY KEY (id, lang_id),
    FOREIGN KEY (id) REFERENCES item(id)
);

-- Metadados do banco
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

# Condições de recompensa padrão
REWARD_CONDITIONS = {
    1: {"en": "Carve", "pt": "Esculpir"},
    2: {"en": "Capture", "pt": "Capturar"},
    3: {"en": "Break Part", "pt": "Quebrar Parte"},
    4: {"en": "Tail Carve", "pt": "Esculpir Cauda"},
    5: {"en": "Palico Bonus", "pt": "Bônus Palico"},
    6: {"en": "Plunderblade", "pt": "Ladroagem"},
    7: {"en": "Shiny Drop", "pt": "Drop Brilhante"},
    8: {"en": "Track", "pt": "Rastro"},
    9: {"en": "Wound", "pt": "Ferida"},
}


class DatabaseBuilder:
    """
    Construtor do banco de dados SQLite.
    """
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.conn: Optional[sqlite3.Connection] = None
    
    def create_database(self):
        """Abre o banco de dados e garante que o schema básico existe."""
        # Não removemos mais o banco existente para preservar dados de armaduras/armas
        self.conn = sqlite3.connect(str(self.output_path))
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        
        # Inserir idiomas
        languages = [
            ('en', 'English', 1),
            ('pt', 'Português', 1),
            ('ja', '日本語', 0),
            ('fr', 'Français', 0),
            ('de', 'Deutsch', 0),
            ('es', 'Español', 0),
        ]
        self.conn.executemany(
            "INSERT OR REPLACE INTO language (id, name, is_complete) VALUES (?, ?, ?)",
            languages
        )
        
        # Inserir condições de recompensa
        for cond_id, names in REWARD_CONDITIONS.items():
            for lang, name in names.items():
                self.conn.execute(
                    "INSERT OR REPLACE INTO monster_reward_condition_text (id, lang_id, name) VALUES (?, ?, ?)",
                    (cond_id, lang, name)
                )
        
        self.conn.commit()
        print(f"Banco de dados criado: {self.output_path}")
    
    def import_from_json(self, json_path: str):
        """
        Importa dados de um arquivo JSON parseado.
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._import_monsters(data.get('monsters', {}))
        self._import_items(data.get('items', {}))
        
        # Atualizar metadados
        self.conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ('import_date', datetime.now().isoformat())
        )
        self.conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ('source', data.get('source', 'unknown'))
        )
        self.conn.commit()
    
    def _import_monsters(self, monsters: Dict[str, Any]):
        """Importa dados de monstros."""
        for monster_id, monster in monsters.items():
            mid = int(monster_id)
            
            # Inserir dados do monstro
            self.conn.execute("""
                INSERT OR REPLACE INTO monster (
                    id, order_id, size,
                    weakness_fire, weakness_water, weakness_thunder, 
                    weakness_ice, weakness_dragon,
                    weakness_poison, weakness_sleep, weakness_paralysis,
                    weakness_blast, weakness_stun,
                    pitfall_trap, shock_trap, vine_trap
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mid, mid, monster.get('size', 'large'),
                monster.get('weakness_fire', 0),
                monster.get('weakness_water', 0),
                monster.get('weakness_thunder', 0),
                monster.get('weakness_ice', 0),
                monster.get('weakness_dragon', 0),
                monster.get('weakness_poison', 0),
                monster.get('weakness_sleep', 0),
                monster.get('weakness_paralysis', 0),
                monster.get('weakness_blast', 0),
                monster.get('weakness_stun', 0),
                1 if monster.get('pitfall_trap') else 0,
                1 if monster.get('shock_trap') else 0,
                1 if monster.get('vine_trap') else 0,
            ))
            
            # Inserir textos (EN)
            if monster.get('name_en'):
                self.conn.execute("""
                    INSERT OR REPLACE INTO monster_text 
                    (id, lang_id, name, ecology, description)
                    VALUES (?, 'en', ?, ?, ?)
                """, (
                    mid,
                    monster.get('name_en', ''),
                    monster.get('ecology', ''),
                    monster.get('description', '')
                ))
            
            # Inserir textos (PT)
            if monster.get('name_pt'):
                self.conn.execute("""
                    INSERT OR REPLACE INTO monster_text 
                    (id, lang_id, name, ecology, description)
                    VALUES (?, 'pt', ?, ?, ?)
                """, (
                    mid,
                    monster.get('name_pt', ''),
                    monster.get('ecology', ''),
                    monster.get('description', '')
                ))
            
            # Inserir hitzones
            for hitzone in monster.get('hitzones', []):
                cursor = self.conn.execute("""
                    INSERT INTO monster_hitzone 
                    (monster_id, cut, impact, shot, fire, water, ice, thunder, dragon, ko)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mid,
                    hitzone.get('cut', 0),
                    hitzone.get('impact', 0),
                    hitzone.get('shot', 0),
                    hitzone.get('fire', 0),
                    hitzone.get('water', 0),
                    hitzone.get('ice', 0),
                    hitzone.get('thunder', 0),
                    hitzone.get('dragon', 0),
                    hitzone.get('ko', 0),
                ))
                hz_id = cursor.lastrowid
                
                # Texto da hitzone
                part_name = hitzone.get('part_name', hitzone.get('part', ''))
                if part_name:
                    self.conn.execute("""
                        INSERT OR REPLACE INTO monster_hitzone_text (id, lang_id, name)
                        VALUES (?, 'en', ?)
                    """, (hz_id, part_name))
        
        self.conn.commit()
        print(f"  Importados {len(monsters)} monstros")
    
    def _import_items(self, items: Dict[str, Any]):
        """Importa dados de itens."""
        for item_id, item in items.items():
            iid = int(item_id)
            
            self.conn.execute("""
                INSERT OR REPLACE INTO item 
                (id, category, rarity, buy_price, sell_price, carry_limit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                iid,
                item.get('category', ''),
                item.get('rarity', 1),
                item.get('buy_price', 0),
                item.get('sell_price', 0),
                item.get('carry_limit', 0),
            ))
            
            # Textos
            if item.get('name_en'):
                self.conn.execute("""
                    INSERT OR REPLACE INTO item_text (id, lang_id, name, description)
                    VALUES (?, 'en', ?, ?)
                """, (iid, item.get('name_en', ''), item.get('description', '')))
            
            if item.get('name_pt'):
                self.conn.execute("""
                    INSERT OR REPLACE INTO item_text (id, lang_id, name, description)
                    VALUES (?, 'pt', ?, ?)
                """, (iid, item.get('name_pt', ''), item.get('description', '')))
        
        self.conn.commit()
        print(f"  Importados {len(items)} itens")
    
    def merge_with_existing(self, existing_db: str):
        """
        Mescla dados do banco existente com os dados extraídos.
        Prioriza dados extraídos do jogo, mas mantém dados do banco existente
        que não foram encontrados na extração.
        """
        if not Path(existing_db).exists():
            print(f"Banco existente não encontrado: {existing_db}")
            return
        
        existing = sqlite3.connect(existing_db)
        existing.row_factory = sqlite3.Row
        
        # Copiar monstros que não existem no novo banco
        cursor = existing.execute("SELECT * FROM monster")
        for row in cursor:
            monster_id = row['id']
            
            # Verificar se já existe
            check = self.conn.execute(
                "SELECT id FROM monster WHERE id = ?", (monster_id,)
            ).fetchone()
            
            if not check:
                # Copiar do banco existente
                cols = [desc[0] for desc in cursor.description]
                placeholders = ', '.join(['?' for _ in cols])
                col_names = ', '.join(cols)
                
                self.conn.execute(
                    f"INSERT INTO monster ({col_names}) VALUES ({placeholders})",
                    tuple(row)
                )
        
        # Copiar textos de monstros
        cursor = existing.execute("SELECT * FROM monster_text")
        for row in cursor:
            try:
                self.conn.execute("""
                    INSERT OR IGNORE INTO monster_text 
                    (id, lang_id, name, ecology, description, alt_state_description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row['id'], row['lang_id'], row['name'],
                    row['ecology'], row['description'],
                    row.get('alt_state_description', '')
                ))
            except:
                pass
        
        # Copiar hitzones
        cursor = existing.execute("SELECT * FROM monster_hitzone")
        for row in cursor:
            # Verificar se já existe uma hitzone similar
            check = self.conn.execute("""
                SELECT id FROM monster_hitzone 
                WHERE monster_id = ? AND cut = ? AND impact = ?
            """, (row['monster_id'], row['cut'], row['impact'])).fetchone()
            
            if not check:
                self.conn.execute("""
                    INSERT INTO monster_hitzone 
                    (monster_id, cut, impact, shot, fire, water, ice, thunder, dragon, ko)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['monster_id'], row['cut'], row['impact'], row['shot'],
                    row['fire'], row['water'], row['ice'], row['thunder'],
                    row['dragon'], row['ko']
                ))
        
        # Copiar textos de hitzone
        cursor = existing.execute("SELECT * FROM monster_hitzone_text")
        for row in cursor:
            try:
                self.conn.execute("""
                    INSERT OR IGNORE INTO monster_hitzone_text (id, lang_id, name)
                    VALUES (?, ?, ?)
                """, (row['id'], row['lang_id'], row['name']))
            except:
                pass
        
        # Copiar itens
        cursor = existing.execute("SELECT * FROM item")
        for row in cursor:
            check = self.conn.execute(
                "SELECT id FROM item WHERE id = ?", (row['id'],)
            ).fetchone()
            
            if not check:
                cols = [desc[0] for desc in cursor.description]
                placeholders = ', '.join(['?' for _ in cols])
                col_names = ', '.join(cols)
                
                self.conn.execute(
                    f"INSERT INTO item ({col_names}) VALUES ({placeholders})",
                    tuple(row)
                )
        
        # Copiar textos de itens
        cursor = existing.execute("SELECT * FROM item_text")
        for row in cursor:
            try:
                self.conn.execute("""
                    INSERT OR IGNORE INTO item_text (id, lang_id, name, description)
                    VALUES (?, ?, ?, ?)
                """, (row['id'], row['lang_id'], row['name'], row.get('description', '')))
            except:
                pass
        
        # Copiar recompensas
        cursor = existing.execute("SELECT * FROM monster_reward")
        for row in cursor:
            try:
                self.conn.execute("""
                    INSERT OR IGNORE INTO monster_reward 
                    (monster_id, condition_id, rank, item_id, stack, percentage)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row['monster_id'], row['condition_id'], row['rank'],
                    row['item_id'], row['stack'], row['percentage']
                ))
            except:
                pass
        
        self.conn.commit()
        existing.close()
        print("Dados mesclados do banco existente")
    
    def close(self):
        """Fecha a conexão com o banco."""
        if self.conn:
            self.conn.close()
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do banco."""
        if not self.conn:
            return {}
        
        stats = {}
        tables = ['monster', 'monster_hitzone', 'item', 'monster_reward']
        
        for table in tables:
            try:
                cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        return stats


def build_database(parsed_data_path: str, 
                   output_path: Optional[str] = None,
                   existing_db: Optional[str] = None) -> str:
    """
    Função principal para construir o banco de dados.
    
    Args:
        parsed_data_path: Caminho para o JSON com dados parseados
        output_path: Caminho de saída para o banco (opcional)
        existing_db: Caminho para banco existente para mesclar (opcional)
    
    Returns:
        Caminho do banco criado
    """
    if output_path is None:
        output_path = str(Path(__file__).parent.parent / "mhw_extracted.db")
    
    print(f"\n=== Construindo banco de dados ===")
    print(f"Fonte: {parsed_data_path}")
    print(f"Destino: {output_path}")
    
    builder = DatabaseBuilder(output_path)
    builder.create_database()
    
    # Importar dados parseados
    if Path(parsed_data_path).exists():
        builder.import_from_json(parsed_data_path)
    
    # Mesclar com banco existente se fornecido
    if existing_db and Path(existing_db).exists():
        print(f"\nMesclando com banco existente: {existing_db}")
        builder.merge_with_existing(existing_db)
    
    # Exibir estatísticas
    stats = builder.get_stats()
    print(f"\n📊 Estatísticas do banco:")
    print(f"   Monstros: {stats.get('monster', 0)}")
    print(f"   Hitzones: {stats.get('monster_hitzone', 0)}")
    print(f"   Itens: {stats.get('item', 0)}")
    print(f"   Recompensas: {stats.get('monster_reward', 0)}")
    
    builder.close()
    
    return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = str(Path(__file__).parent / "extracted_data" / "parsed_data.json")
    
    existing = str(Path(__file__).parent.parent / "mhw.db")
    
    build_database(json_path, existing_db=existing)
