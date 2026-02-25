from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Skill:
    name: str
    level: int
    description: Optional[str] = None

@dataclass
class Decoration:
    id: int
    name: str
    rarity: int
    slot: int
    skills: List[Skill] = field(default_factory=list)

    @classmethod
    def from_db_row(cls, row):
        # Mapeia as tuplas/dicionários do SQLite para o modelo
        skills = [Skill(name=row['skill_name'], level=row['skilltree_level'])]
        
        # sqlite3.Row não tem .get(), usamos tratamento simples
        try:
            if row['skilltree2_id']:
                # Se tiver uma segunda skill (joias híbridas)
                pass 
        except (IndexError, KeyError):
            pass
        
        return cls(
            id=row['id'],
            name=row['decoration_name'],
            rarity=row['rarity'],
            slot=row['slot'],
            skills=skills
        )

@dataclass
class ArmorPiece:
    name: str
    type: str # 'Head', 'Chest', etc.
    slots: List[int]
    innate_skills: List[Skill]
    decorations: List[Optional[Decoration]] = field(default_factory=list)

    def __post_init__(self):
        if not self.decorations:
            # Garante que a lista tenha o tamanho correto com None para slots vazios
            self.decorations = [None] * len(self.slots) # type: ignore

@dataclass
class BuildData:
    weapon_name: str
    armor: List[ArmorPiece]
    weapon_slots: List[int] = field(default_factory=list)
