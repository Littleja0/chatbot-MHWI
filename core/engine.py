from core.database_manager import DatabaseManager
from core.models import BuildData, Decoration, Skill, ArmorPiece
from typing import List, Dict

class BuildEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def suggest_build(self, build_data: BuildData, skill_priorities: List[str]):
        """
        Otimiza a build preenchendo os slots vazios com joias baseadas nas prioridades.
        """
        print(f"\n🚀 OTIMIZANDO BUILD: {build_data.weapon_name}")
        print("-" * 50)

        for piece in build_data.armor:
            print(f"[Peça]: {piece.name}")
            innate_names = [f"{s.name} Lv{s.level}" for s in piece.innate_skills]
            print(f"  Nativas: {', '.join(innate_names)}")
            
            for i, slot_lvl in enumerate(piece.slots):
                # Tenta preencher cada slot com a melhor joia possível das prioridades
                found = False
                for target_skill in skill_priorities:
                    possible_decos = self.db.get_decorations_by_skill(target_skill, max_slot=slot_lvl)
                    
                    if possible_decos:
                        # Pega a primeira (ordenada por raridade no DB Manager)
                        best_row = possible_decos[0]
                        deco = Decoration.from_db_row(best_row)
                        piece.decorations[i] = deco
                        print(f"  Slot {i+1} (Lv{slot_lvl}): ⭐ {deco.name} (Rarity {deco.rarity})")
                        found = True
                        break
                
                if not found:
                    print(f"  Slot {i+1} (Lv{slot_lvl}): 🔹 Vazio (Nenhuma joia prioritária disponível)")

        self._print_summary(build_data)

    def _print_summary(self, build_data: BuildData):
        print("\n" + "=" * 50)
        print("RESUMO DA BUILD OTIMIZADA:")
        
        all_skills: Dict[str, int] = {}
        
        # Consolida skills
        for piece in build_data.armor:
            for s in piece.innate_skills:
                all_skills[s.name] = all_skills.get(s.name, 0) + s.level
            for deco in piece.decorations:
                if deco:
                    for s in deco.skills:
                        all_skills[s.name] = all_skills.get(s.name, 0) + s.level
        
        for name, level in sorted(all_skills.items(), key=lambda x: x[1], reverse=True):
            print(f"- {name}: Lv{level}")
        print("=" * 50)

if __name__ == "__main__":
    db = DatabaseManager()
    engine = BuildEngine(db)
    
    # Exemplo de uso simulando o protótipo mas com a nova estrutura
    data = BuildData(
        weapon_name="Lightbreak Blade (Great Sword)",
        armor=[
            ArmorPiece(name="Kaiser Crown β+", type="Head", slots=[4, 1], innate_skills=[Skill("Critical Eye", 2)]),
            ArmorPiece(name="Kaiser Mail β+", type="Chest", slots=[4, 1, 1], innate_skills=[Skill("Weakness Exploit", 1)]),
        ]
    )
    
    priorities = ["Attack Boost", "Critical Eye"]
    engine.suggest_build(data, priorities)
    db.close()
