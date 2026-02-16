"""
rag_loader.py — Loader inteligente de XMLs para o RAG do MHW Chatbot.

Em vez de jogar XML bruto no LlamaIndex (que não entende a estrutura),
este módulo parseia os XMLs, junta dados relacionados por ID, e gera
documentos de texto legíveis e semânticos que o RAG consegue indexar.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from llama_index.core import Document  # type: ignore

RAG_PATH = Path("rag")
LANGS = ["pt", "en"]


def _parse_xml(filename: str) -> list[dict]:
    """Parseia um XML e retorna lista de dicts (um por DATA_RECORD)."""
    path = RAG_PATH / filename
    if not path.exists():
        return []
    try:
        tree = ET.parse(path)
        records = []
        for rec in tree.getroot().findall("DATA_RECORD"):
            data = {}
            for child in rec:
                data[child.tag] = child.text or ""
            records.append(data)
        return records
    except Exception as e:
        print(f"⚠️ Erro ao parsear {filename}: {e}")
        return []


def _build_text_lookup(filename: str, key: str = "id") -> dict:
    """
    Cria lookup {id -> {lang -> {field: value}}} a partir de um XML de texto.
    """
    records = _parse_xml(filename)
    lookup: dict = {}
    for rec in records:
        rid = rec.get(key, "")
        lang = rec.get("lang_id", "")
        if lang not in LANGS:
            continue
        if rid not in lookup:
            lookup[rid] = {}
        fields = {k: v for k, v in rec.items() if k not in (key, "lang_id") and v}
        lookup[rid][lang] = fields
    return lookup


def _group_by(records: list[dict], key: str) -> dict:
    """Agrupa registros por um campo chave."""
    grouped: dict = {}
    for r in records:
        k = r.get(key, "")
        if k not in grouped:
            grouped[k] = []
        grouped[k].append(r)
    return grouped


def _get_name(texts: dict, field: str = "name") -> tuple[str, str]:
    """Retorna (name_pt, name_en) de um lookup de texto."""
    name_pt = texts.get("pt", {}).get(field, "")
    name_en = texts.get("en", {}).get(field, "")
    return name_pt, name_en


def _display_name(texts: dict, field: str = "name") -> str:
    """Retorna o nome de exibição (PT preferencial, fallback EN)."""
    pt, en = _get_name(texts, field)
    return pt or en


def _weakness_stars(value: str) -> str:
    try:
        n = int(value)
        if n == 0:
            return "✗"
        return "★" * n
    except (ValueError, TypeError):
        return "—"


def _build_recipe_lookup(item_text: dict) -> dict:
    """
    Cria lookup {recipe_id -> "Item A x2, Item B x1"}
    usando recipe_item.xml e item_text.
    """
    recipe_items = _parse_xml("recipe_item.xml")
    grouped = _group_by(recipe_items, "recipe_id")
    lookup: dict = {}
    for rid, items in grouped.items():
        parts = []
        for ri in items:
            iid = ri.get("item_id", "")
            qty = ri.get("quantity", "1")
            it = item_text.get(iid, {})
            iname = _display_name(it) or f"Item #{iid}"
            parts.append(f"{iname} x{qty}")
        lookup[rid] = ", ".join(parts)
    return lookup


# ============================================================
# MONSTROS
# ============================================================
def _load_monsters() -> list[Document]:
    docs = []
    monsters = _parse_xml("monster.xml")
    text_lookup = _build_text_lookup("monster_text.xml")

    # Habitats
    habitat_by_monster = _group_by(_parse_xml("monster_habitat.xml"), "monster_id")
    loc_text = _build_text_lookup("location_text.xml")

    # Recompensas
    reward_by_monster = _group_by(_parse_xml("monster_reward.xml"), "monster_id")
    reward_cond_text = _build_text_lookup("monster_reward_condition_text.xml")
    item_text = _build_text_lookup("item_text.xml")

    # Hitzones
    hitzone_by_monster = _group_by(_parse_xml("monster_hitzone.xml"), "monster_id")
    hitzone_text = _build_text_lookup("monster_hitzone_text.xml")

    # Breaks
    break_by_monster = _group_by(_parse_xml("monster_break.xml"), "monster_id")
    break_text = _build_text_lookup("monster_break_text.xml")

    for m in monsters:
        mid = m.get("id", "")
        texts = text_lookup.get(mid, {})
        name_pt, name_en = _get_name(texts)
        if not name_en and not name_pt:
            continue

        name = name_pt or name_en
        size = m.get("size", "unknown")

        lines = [f"=== MONSTRO: {name} ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en} | Nome (PT): {name_pt}")
        lines.append(f"Tamanho: {size}")

        # Descrição
        desc_pt = texts.get("pt", {}).get("description", "")
        desc_en = texts.get("en", {}).get("description", "")
        if desc_pt:
            lines.append(f"Descrição: {desc_pt}")
        elif desc_en:
            lines.append(f"Description: {desc_en}")

        # Habitats
        habitats = habitat_by_monster.get(mid, [])
        if habitats:
            loc_names = []
            for h in habitats:
                lid = h.get("location_id", "")
                lt = loc_text.get(lid, {})
                lname = _display_name(lt)
                if lname and lname not in loc_names:
                    loc_names.append(lname)
            if loc_names:
                lines.append(f"Localizações: {', '.join(loc_names)}")

        # Armadilhas
        traps = []
        if m.get("pitfall_trap") == "1":
            traps.append("Armadilha de Fosso")
        if m.get("shock_trap") == "1":
            traps.append("Armadilha de Choque")
        if m.get("vine_trap") == "1":
            traps.append("Armadilha de Vinha")
        if traps:
            lines.append(f"Armadilhas efetivas: {', '.join(traps)}")
        elif size == "large":
            lines.append("Armadilhas: Nenhuma efetiva")

        # Fraquezas elementais
        if m.get("has_weakness") == "1":
            lines.append("--- Fraquezas Elementais ---")
            for label, key in [("Fogo", "weakness_fire"), ("Água", "weakness_water"),
                               ("Gelo", "weakness_ice"), ("Trovão", "weakness_thunder"),
                               ("Dragão", "weakness_dragon")]:
                val = m.get(key, "")
                if val:
                    lines.append(f"  {label}: {_weakness_stars(val)}")
            status_parts = []
            for label, key in [("Veneno", "weakness_poison"), ("Sono", "weakness_sleep"),
                               ("Paralisia", "weakness_paralysis"), ("Explosão", "weakness_blast"),
                               ("Atordoamento", "weakness_stun")]:
                val = m.get(key, "")
                if val and val != "0":
                    status_parts.append(f"{label}({_weakness_stars(val)})")
            if status_parts:
                lines.append(f"  Status: {', '.join(status_parts)}")

        # Fraquezas alternativas
        if m.get("has_alt_weakness") == "1":
            lines.append("--- Fraquezas Alternativas (Estado Especial) ---")
            for label, key in [("Fogo", "alt_weakness_fire"), ("Água", "alt_weakness_water"),
                               ("Gelo", "alt_weakness_ice"), ("Trovão", "alt_weakness_thunder"),
                               ("Dragão", "alt_weakness_dragon")]:
                val = m.get(key, "")
                if val:
                    lines.append(f"  {label}: {_weakness_stars(val)}")

        # Ameaças
        ailment_map = {
            "ailment_fireblight": "Praga de Fogo", "ailment_waterblight": "Praga de Água",
            "ailment_thunderblight": "Praga de Trovão", "ailment_iceblight": "Praga de Gelo",
            "ailment_dragonblight": "Praga de Dragão", "ailment_blastblight": "Praga de Explosão",
            "ailment_poison": "Envenenamento", "ailment_sleep": "Sono",
            "ailment_paralysis": "Paralisia", "ailment_bleed": "Sangramento",
            "ailment_stun": "Atordoamento", "ailment_mud": "Lama",
            "ailment_effluvia": "Efúvio",
        }
        ailments = [label for key, label in ailment_map.items() if m.get(key) == "1"]
        if ailments:
            lines.append(f"Ameaças: {', '.join(ailments)}")
        for tag, label in [("ailment_roar", "Rugido"), ("ailment_wind", "Pressão de Vento"),
                           ("ailment_tremor", "Tremor")]:
            val = m.get(tag, "")
            if val and val != "0":
                lines.append(f"{label}: Nível {val}")

        # Hitzones
        hitzones = hitzone_by_monster.get(mid, [])
        if hitzones:
            lines.append("--- Zonas de Dano ---")
            for hz in hitzones:
                hz_id = hz.get("id", "")
                ht = hitzone_text.get(hz_id, {})
                hz_name = _display_name(ht) or f"Zona {hz_id}"
                cut = hz.get("cut", "0")
                impact = hz.get("impact", "0")
                shot = hz.get("shot", "0")
                fire = hz.get("fire", "0")
                water = hz.get("water", "0")
                ice = hz.get("ice", "0")
                thunder = hz.get("thunder", "0")
                dragon = hz.get("dragon", "0")
                lines.append(f"  {hz_name}: Corte={cut} Impacto={impact} Projétil={shot} | Fogo={fire} Água={water} Gelo={ice} Trovão={thunder} Dragão={dragon}")

        # Partes quebráveis
        breaks = break_by_monster.get(mid, [])
        if breaks:
            lines.append("--- Partes Quebráveis ---")
            for b in breaks:
                bid = b.get("id", "")
                bt = break_text.get(bid, {})
                bname = _display_name(bt) or f"Parte {bid}"
                flinch = b.get("flinch", "")
                wound = b.get("wound", "")
                sever = b.get("sever", "")
                parts = [f"  {bname}:"]
                if flinch:
                    parts.append(f"Hesitação={flinch}")
                if wound:
                    parts.append(f"Ferida={wound}")
                if sever:
                    parts.append(f"Corte={sever}")
                lines.append(" ".join(parts))

        # Recompensas (top items únicos)
        rewards = reward_by_monster.get(mid, [])
        if rewards:
            lines.append("--- Recompensas (Drops) ---")
            seen: set = set()
            count = 0
            for rw in rewards:
                item_id = rw.get("item_id", "")
                it = item_text.get(item_id, {})
                iname = _display_name(it)
                if not iname or iname in seen:
                    continue
                seen.add(iname)
                cond_id = rw.get("condition_id", "")
                ct = reward_cond_text.get(cond_id, {})
                cname = _display_name(ct)
                rank = rw.get("rank", "")
                pct = rw.get("percentage", "")
                stack = rw.get("stack", "1")
                parts = [f"  {iname}"]
                if rank:
                    parts.append(f"Rank={rank}")
                if cname:
                    parts.append(f"de={cname}")
                if pct:
                    parts.append(f"{pct}%")
                if stack and stack != "1":
                    parts.append(f"x{stack}")
                lines.append(" | ".join(parts))
                count += 1
                if count >= 20:
                    break

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "monster", "monster_id": mid, "name_pt": name_pt, "name_en": name_en, "size": size},
        ))
    return docs


# ============================================================
# ARMAS
# ============================================================
def _load_weapons() -> list[Document]:
    docs = []
    weapons = _parse_xml("weapon.xml")
    weapon_text = _build_text_lookup("weapon_text.xml")
    item_text = _build_text_lookup("item_text.xml")
    recipe_lookup = _build_recipe_lookup(item_text)
    # Ammo para bowguns
    ammo_by_weapon = _group_by(_parse_xml("weapon_ammo.xml"), "id")
    # Melodies para hunting horn
    melody_records = _parse_xml("weapon_melody.xml")
    melody_text = _build_text_lookup("weapon_melody_text.xml")
    melody_notes_records = _parse_xml("weapon_melody_notes.xml")
    melody_by_weapon = _group_by(melody_records, "id")
    # Skills embutidas em armas
    weapon_skills = _parse_xml("weapon_skill.xml")
    wskill_by_weapon = _group_by(weapon_skills, "weapon_id")
    skilltree_text = _build_text_lookup("skilltree_text.xml")

    for w in weapons:
        wid = w.get("id", "")
        texts = weapon_text.get(wid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        wtype = w.get("weapon_type", "unknown")
        lines = [f"=== ARMA: {name} ({wtype}) ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        attack = w.get("attack", "")
        affinity = w.get("affinity", "")
        elem1 = w.get("element1", "")
        elem1_atk = w.get("element1_attack", "")
        elem2 = w.get("element2", "")
        elem2_atk = w.get("element2_attack", "")
        elem_hidden = w.get("element_hidden", "")
        elderseal = w.get("elderseal", "")
        defense = w.get("defense", "")
        rarity = w.get("rarity", "")
        sharpness = w.get("sharpness", "")

        if attack:
            lines.append(f"Ataque: {attack}")
        if affinity and affinity != "0":
            lines.append(f"Afinidade: {affinity}%")
        if elem1 and elem1_atk:
            hidden = " (Oculto)" if elem_hidden == "1" else ""
            lines.append(f"Elemento: {elem1} ({elem1_atk}){hidden}")
        if elem2 and elem2_atk:
            lines.append(f"Elemento 2: {elem2} ({elem2_atk})")
        if elderseal and elderseal != "None":
            lines.append(f"Selo Ancião: {elderseal}")
        if defense and defense != "0":
            lines.append(f"Bônus Defesa: +{defense}")
        if rarity:
            lines.append(f"Raridade: {rarity}")

        slots = [w.get(f"slot_{i}", "0") for i in range(1, 4)]
        slots = [s for s in slots if s and s != "0"]
        if slots:
            lines.append(f"Slots: [{', '.join(slots)}]")

        if sharpness:
            lines.append(f"Afiação: {sharpness}")

        # Skills embutidas
        wskills = wskill_by_weapon.get(wid, [])
        if wskills:
            skill_names = []
            for ws in wskills:
                st_id = ws.get("skilltree_id", "")
                level = ws.get("level", "1")
                st = skilltree_text.get(st_id, {})
                sname = _display_name(st)
                if sname:
                    skill_names.append(f"{sname} +{level}")
            if skill_names:
                lines.append(f"Skills: {', '.join(skill_names)}")

        # Ammo (bowgun)
        ammos = ammo_by_weapon.get(wid, [])
        if ammos:
            ammo_parts = []
            for a in ammos:
                ammo_type = a.get("ammo_type", "")
                clip = a.get("clip", "0")
                if ammo_type and clip != "0":
                    ammo_parts.append(f"{ammo_type}({clip})")
            if ammo_parts:
                lines.append(f"Munição: {', '.join(ammo_parts)}")

        # Receitas de crafting
        create_rid = w.get("create_recipe_id", "")
        upgrade_rid = w.get("upgrade_recipe_id", "")
        if create_rid and create_rid in recipe_lookup:
            lines.append(f"Materiais (Criar): {recipe_lookup[create_rid]}")
        if upgrade_rid and upgrade_rid in recipe_lookup:
            lines.append(f"Materiais (Upgrade): {recipe_lookup[upgrade_rid]}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "weapon", "weapon_type": wtype, "name": name},
        ))
    return docs


# ============================================================
# ARMADURAS
# ============================================================
def _load_armor() -> list[Document]:
    docs = []
    armors = _parse_xml("armor.xml")
    armor_text = _build_text_lookup("armor_text.xml")
    armor_skills = _parse_xml("armor_skill.xml")
    skilltree_text = _build_text_lookup("skilltree_text.xml")
    skill_by_armor = _group_by(armor_skills, "armor_id")
    item_text = _build_text_lookup("item_text.xml")
    recipe_lookup = _build_recipe_lookup(item_text)

    for a in armors:
        aid = a.get("id", "")
        texts = armor_text.get(aid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"=== ARMADURA: {name} ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        rank = a.get("rank", "")
        rarity = a.get("rarity", "")
        atype = a.get("armor_type", "")
        armorset_id = a.get("armorset_id", "")

        if rank:
            lines.append(f"Rank: {rank}")
        if rarity:
            lines.append(f"Raridade: {rarity}")
        if atype:
            lines.append(f"Tipo: {atype}")

        defense = a.get("defense_base", "")
        defense_max = a.get("defense_max", "")
        defense_aug = a.get("defense_augment_max", "")
        if defense:
            parts = [f"Defesa: {defense}"]
            if defense_max:
                parts.append(f"máx {defense_max}")
            if defense_aug:
                parts.append(f"aug {defense_aug}")
            lines.append(" → ".join(parts))

        # Resistências
        res_parts = []
        for elem, key in [("Fogo", "fire"), ("Água", "water"), ("Gelo", "ice"),
                          ("Trovão", "thunder"), ("Dragão", "dragon")]:
            val = a.get(key, "0")
            if val and val != "0":
                res_parts.append(f"{elem}={val}")
        if res_parts:
            lines.append(f"Resistências: {', '.join(res_parts)}")

        # Slots
        slots = [a.get(f"slot_{i}", "0") for i in range(1, 4)]
        slots = [s for s in slots if s and s != "0"]
        if slots:
            lines.append(f"Slots: [{', '.join(slots)}]")

        # Skills
        skills = skill_by_armor.get(aid, [])
        if skills:
            skill_names = []
            for s in skills:
                st_id = s.get("skilltree_id", "")
                level = s.get("level", "1")
                st = skilltree_text.get(st_id, {})
                sname = _display_name(st)
                if sname:
                    skill_names.append(f"{sname} +{level}")
            if skill_names:
                lines.append(f"Skills: {', '.join(skill_names)}")

        # Receitas de crafting
        create_rid = a.get("recipe_id", "")
        if create_rid and create_rid in recipe_lookup:
            lines.append(f"Materiais: {recipe_lookup[create_rid]}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "armor", "name": name, "armorset_id": armorset_id},
        ))
    return docs


# ============================================================
# SETS DE ARMADURA + BÔNUS
# ============================================================
def _load_armorsets() -> list[Document]:
    docs = []
    armorsets = _parse_xml("armorset.xml")
    armorset_text = _build_text_lookup("armorset_text.xml")
    bonus_text = _build_text_lookup("armorset_bonus_text.xml")
    bonus_skills = _parse_xml("armorset_bonus_skill.xml")
    bonus_skill_by_set = _group_by(bonus_skills, "setbonus_id")
    skilltree_text = _build_text_lookup("skilltree_text.xml")
    # Armaduras para listar peças
    armor_text = _build_text_lookup("armor_text.xml")
    armors = _parse_xml("armor.xml")
    armor_by_set = _group_by(armors, "armorset_id")

    for aset in armorsets:
        sid = aset.get("id", "")
        texts = armorset_text.get(sid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"=== SET DE ARMADURA: {name} ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        rank = aset.get("rank", "")
        if rank:
            lines.append(f"Rank: {rank}")

        # Peças do set
        pieces = armor_by_set.get(sid, [])
        if pieces:
            piece_names = []
            for p in pieces:
                pid = p.get("id", "")
                pt = armor_text.get(pid, {})
                pname = _display_name(pt)
                if pname:
                    piece_names.append(pname)
            if piece_names:
                lines.append(f"Peças: {', '.join(piece_names)}")

        # Bônus do set
        bonus_id = aset.get("armorset_bonus_id", "")
        if bonus_id:
            bt = bonus_text.get(bonus_id, {})
            bname = _display_name(bt)
            if bname:
                lines.append(f"Bônus do Set: {bname}")
            bdesc_pt = bt.get("pt", {}).get("description", "")
            bdesc_en = bt.get("en", {}).get("description", "")
            if bdesc_pt:
                lines.append(f"Descrição do Bônus: {bdesc_pt}")
            elif bdesc_en:
                lines.append(f"Descrição do Bônus: {bdesc_en}")

            # Skills do bônus
            bskills = bonus_skill_by_set.get(bonus_id, [])
            if bskills:
                for bs in bskills:
                    st_id = bs.get("skilltree_id", "")
                    required = bs.get("required", "")
                    st = skilltree_text.get(st_id, {})
                    sname = _display_name(st)
                    if sname:
                        lines.append(f"  {required} peças → {sname}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "armorset", "name": name},
        ))
    return docs


# ============================================================
# AMULETOS (CHARMS)
# ============================================================
def _load_charms() -> list[Document]:
    docs = []
    charms = _parse_xml("charm.xml")
    charm_text = _build_text_lookup("charm_text.xml")
    charm_skills = _parse_xml("charm_skill.xml")
    skill_by_charm = _group_by(charm_skills, "charm_id")
    skilltree_text = _build_text_lookup("skilltree_text.xml")
    item_text = _build_text_lookup("item_text.xml")
    recipe_lookup = _build_recipe_lookup(item_text)

    for c in charms:
        cid = c.get("id", "")
        texts = charm_text.get(cid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"=== AMULETO: {name} ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        rarity = c.get("rarity", "")
        if rarity:
            lines.append(f"Raridade: {rarity}")

        skills = skill_by_charm.get(cid, [])
        if skills:
            skill_names = []
            for s in skills:
                st_id = s.get("skilltree_id", "")
                level = s.get("level", "1")
                st = skilltree_text.get(st_id, {})
                sname = _display_name(st)
                if sname:
                    skill_names.append(f"{sname} +{level}")
            if skill_names:
                lines.append(f"Skills: {', '.join(skill_names)}")

        # Receitas de crafting
        create_rid = c.get("recipe_id", "")
        if create_rid and create_rid in recipe_lookup:
            lines.append(f"Materiais: {recipe_lookup[create_rid]}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "charm", "name": name},
        ))
    return docs


# ============================================================
# DECORAÇÕES (JEWELS)
# ============================================================
def _load_decorations() -> list[Document]:
    docs = []
    decos = _parse_xml("decoration.xml")
    deco_text = _build_text_lookup("decoration_text.xml")
    skilltree_text = _build_text_lookup("skilltree_text.xml")

    for d in decos:
        did = d.get("id", "")
        texts = deco_text.get(did, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"DECORAÇÃO: {name}"]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        slot = d.get("slot", "")
        rarity = d.get("rarity", "")
        if slot:
            lines.append(f"Slot: {slot}")
        if rarity:
            lines.append(f"Raridade: {rarity}")

        st_id = d.get("skilltree_id", "")
        if st_id:
            st = skilltree_text.get(st_id, {})
            sname = _display_name(st)
            if sname:
                lines.append(f"Skill: {sname}")

        # Drop rates (Feystones)
        rates = []
        for key, label in [
            ("mysterious_feystone_percent", "Misteriosa"),
            ("glowing_feystone_percent", "Cintilante"),
            ("worn_feystone_percent", "Gasta"),
            ("warped_feystone_percent", "Entalhada"),
            ("ancient_feystone_percent", "Antiga"),
            ("carved_feystone_percent", "Gravada"),
            ("sealed_feystone_percent", "Selada")
        ]:
            val = d.get(key, "")
            if val and val != "0.0" and val != "0":
                rates.append(f"{label}: {val}%")
        
        if rates:
            lines.append("Drop Rates (Chances por Pedra de Feitiço):")
            for r in rates:
                lines.append(f"  - {r}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "decoration", "name": name},
        ))
    return docs


# ============================================================
# CONHECIMENTO MANUAL (MANTOS, DROPS, ETC)
# ============================================================
def _load_manual_knowledge() -> list[Document]:
    docs = []
    records = _parse_xml("manual_knowledge.xml")
    for rec in records:
        content = rec.get("content", "")
        topic = rec.get("topic", "")
        if content:
            docs.append(Document(
                text=f"=== {topic} ===\n{content}",
                metadata={"source": "manual", "topic": topic}
            ))
    return docs


# ============================================================
# CATÁLOGO DE JOIAS (ESTRUTURADO)
# ============================================================
def _load_jewel_catalog() -> list[Document]:
    docs = []
    records = _parse_xml("jewel_catalog.xml")
    for rec in records:
        content = rec.get("content", "")
        topic = rec.get("topic", "")
        if content:
            docs.append(Document(
                text=f"=== {topic} ===\n{content}",
                metadata={"source": "jewel_catalog", "topic": topic}
            ))
    return docs


# ============================================================
# ITENS
# ============================================================
def _load_items() -> list[Document]:
    docs = []
    items = _parse_xml("item.xml")
    item_text = _build_text_lookup("item_text.xml")
    # Combinações de itens de campo
    combinations = _parse_xml("item_combination.xml")

    # Lookup combinações: result_id -> lista de ingredientes
    combo_lookup: dict = {}
    for c in combinations:
        result = c.get("result_id", "")
        if result not in combo_lookup:
            combo_lookup[result] = []
        combo_lookup[result].append(c)

    for item in items:
        iid = item.get("id", "")
        texts = item_text.get(iid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"ITEM: {name}"]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        desc_pt = texts.get("pt", {}).get("description", "")
        desc_en = texts.get("en", {}).get("description", "")
        desc = desc_pt or desc_en
        if desc:
            lines.append(f"Descrição: {desc}")

        rarity = item.get("rarity", "")
        category = item.get("category", "")
        subcategory = item.get("subcategory", "")
        if rarity:
            lines.append(f"Raridade: {rarity}")
        if category:
            lines.append(f"Categoria: {category}")
        if subcategory:
            lines.append(f"Subcategoria: {subcategory}")

        buy = item.get("buy_price", "")
        sell = item.get("sell_price", "")
        if buy and buy != "0":
            lines.append(f"Compra: {buy}z")
        if sell and sell != "0":
            lines.append(f"Venda: {sell}z")

        # Receitas para craftar este item
        combos = combo_lookup.get(iid, [])
        if combos:
            for combo in combos:
                first = combo.get("first_id", "")
                second = combo.get("second_id", "")
                qty = combo.get("quantity", "1")
                first_t = item_text.get(first, {})
                fname = _display_name(first_t) or f"Item #{first}"
                if second:
                    second_t = item_text.get(second, {})
                    sname = _display_name(second_t) or f"Item #{second}"
                    lines.append(f"Combinação: {fname} + {sname} = {name} x{qty}")
                else:
                    lines.append(f"Combinação: {fname} = {name} x{qty}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "item", "name": name},
        ))
    return docs


# ============================================================
# SKILLS
# ============================================================
def _load_skills() -> list[Document]:
    docs = []
    skills = _parse_xml("skill.xml")
    skilltree_text = _build_text_lookup("skilltree_text.xml")

    by_tree = _group_by(skills, "skilltree_id")

    for stid, levels in by_tree.items():
        texts = skilltree_text.get(stid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"=== SKILL: {name} ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        desc_pt = texts.get("pt", {}).get("description", "")
        desc_en = texts.get("en", {}).get("description", "")
        desc = desc_pt or desc_en
        if desc:
            lines.append(f"Descrição: {desc}")

        lines.append(f"Nível Máximo: {len(levels)}")

        # Detalhe por nível
        for lvl in sorted(levels, key=lambda x: x.get("level", "0")):
            level_num = lvl.get("level", "")
            lvl_desc_pt = lvl.get("description", "")  # inline descriptions
            if level_num:
                lines.append(f"  Nível {level_num}: {lvl_desc_pt}" if lvl_desc_pt else f"  Nível {level_num}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "skill", "name": name},
        ))
    return docs


# ============================================================
# QUESTS
# ============================================================
def _load_quests() -> list[Document]:
    docs = []
    quests = _parse_xml("quest.xml")
    quest_text = _build_text_lookup("quest_text.xml")
    # Monstros por quest
    quest_monsters = _parse_xml("quest_monster.xml")
    qm_by_quest = _group_by(quest_monsters, "quest_id")
    monster_text = _build_text_lookup("monster_text.xml")
    # Recompensas por quest
    quest_rewards = _parse_xml("quest_reward.xml")
    qr_by_quest = _group_by(quest_rewards, "quest_id")
    item_text = _build_text_lookup("item_text.xml")
    loc_text = _build_text_lookup("location_text.xml")

    for q in quests:
        qid = q.get("id", "")
        texts = quest_text.get(qid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"QUEST: {name}"]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        rank = q.get("rank", "")
        stars = q.get("stars", "")
        category = q.get("category", "")
        loc_id = q.get("location_id", "")

        if rank:
            lines.append(f"Rank: {rank}")
        if stars:
            try:
                lines.append(f"Estrelas: {'★' * int(stars)}")
            except ValueError:
                lines.append(f"Estrelas: {stars}")
        if category:
            lines.append(f"Categoria: {category}")
        if loc_id:
            lt = loc_text.get(loc_id, {})
            lname = _display_name(lt)
            if lname:
                lines.append(f"Local: {lname}")

        # Objetivo
        obj_pt = texts.get("pt", {}).get("objective", "")
        obj_en = texts.get("en", {}).get("objective", "")
        obj = obj_pt or obj_en
        if obj:
            lines.append(f"Objetivo: {obj}")

        desc_pt = texts.get("pt", {}).get("description", "")
        desc_en = texts.get("en", {}).get("description", "")
        desc = desc_pt or desc_en
        if desc:
            lines.append(f"Descrição: {desc}")

        # Monstros da quest
        qmonsters = qm_by_quest.get(qid, [])
        if qmonsters:
            mnames = []
            for qm in qmonsters:
                mid = qm.get("monster_id", "")
                mt = monster_text.get(mid, {})
                mname = _display_name(mt)
                qty = qm.get("quantity", "1")
                if mname:
                    mnames.append(f"{mname}" + (f" x{qty}" if qty != "1" else ""))
            if mnames:
                lines.append(f"Monstros: {', '.join(mnames)}")

        # Recompensas (top 10)
        qrewards = qr_by_quest.get(qid, [])
        if qrewards:
            lines.append("Recompensas:")
            seen: set = set()
            count = 0
            for qr in qrewards:
                item_id = qr.get("item_id", "")
                it = item_text.get(item_id, {})
                iname = _display_name(it)
                if not iname or iname in seen:
                    continue
                seen.add(iname)
                pct = qr.get("percentage", "")
                stack = qr.get("stack", "1")
                parts = [f"  {iname}"]
                if pct:
                    parts.append(f"{pct}%")
                if stack and stack != "1":
                    parts.append(f"x{stack}")
                lines.append(" | ".join(parts))
                count += 1
                if count >= 10:
                    break

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "quest", "name": name},
        ))
    return docs


# ============================================================
# KINSECTS (INSECT GLAIVE)
# ============================================================
def _load_kinsects() -> list[Document]:
    docs = []
    kinsects = _parse_xml("kinsect.xml")
    kinsect_text = _build_text_lookup("kinsect_text.xml")

    for k in kinsects:
        kid = k.get("id", "")
        texts = kinsect_text.get(kid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"KINSECT: {name}"]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        rarity = k.get("rarity", "")
        attack_type = k.get("attack_type", "")
        dust_effect = k.get("dust_effect", "")
        power = k.get("power", "")
        speed = k.get("speed", "")
        heal = k.get("heal", "")

        if rarity:
            lines.append(f"Raridade: {rarity}")
        if attack_type:
            lines.append(f"Tipo de Ataque: {attack_type}")
        if dust_effect:
            lines.append(f"Efeito de Pó: {dust_effect}")
        if power:
            lines.append(f"Poder: {power}")
        if speed:
            lines.append(f"Velocidade: {speed}")
        if heal:
            lines.append(f"Cura: {heal}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "kinsect", "name": name},
        ))
    return docs


# ============================================================
# FERRAMENTAS (MANTLES / BOOSTERS)
# ============================================================
def _load_tools() -> list[Document]:
    docs = []
    tools = _parse_xml("tool.xml")
    tool_text = _build_text_lookup("tool_text.xml")

    for t in tools:
        tid = t.get("id", "")
        texts = tool_text.get(tid, {})
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"=== FERRAMENTA: {name} ==="]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        desc_pt = texts.get("pt", {}).get("description", "")
        desc_en = texts.get("en", {}).get("description", "")
        desc = desc_pt or desc_en
        if desc:
            lines.append(f"Descrição: {desc}")

        tool_type = t.get("tool_type", "")
        duration = t.get("duration", "")
        recharge = t.get("recharge", "")

        if tool_type:
            lines.append(f"Tipo: {tool_type}")
        if duration and duration != "0":
            lines.append(f"Duração: {duration}s")
        if recharge and recharge != "0":
            lines.append(f"Recarga: {recharge}s")

        # Slots
        slots = [t.get(f"slot_{i}", "0") for i in range(1, 4)]
        slots = [s for s in slots if s and s != "0"]
        if slots:
            lines.append(f"Slots: [{', '.join(slots)}]")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "tool", "name": name},
        ))
    return docs


# ============================================================
# LOCALIZAÇÕES
# ============================================================
def _load_locations() -> list[Document]:
    docs = []
    loc_text = _build_text_lookup("location_text.xml")
    camp_text = _build_text_lookup("location_camp_text.xml")
    loc_items = _parse_xml("location_item.xml")
    item_text = _build_text_lookup("item_text.xml")
    loc_item_by_loc = _group_by(loc_items, "location_id")

    for lid, texts in loc_text.items():
        name_pt, name_en = _get_name(texts)
        if not name_pt and not name_en:
            continue

        name = name_pt or name_en
        lines = [f"LOCALIZAÇÃO: {name}"]
        if name_pt and name_en and name_pt != name_en:
            lines.append(f"Nome (EN): {name_en}")

        # Itens coletáveis nessa localização
        litems = loc_item_by_loc.get(lid, [])
        if litems:
            item_names_seen: set = set()
            item_list = []
            for li in litems:
                iid = li.get("item_id", "")
                it = item_text.get(iid, {})
                iname = _display_name(it)
                area = li.get("area", "")
                if iname and iname not in item_names_seen:
                    item_names_seen.add(iname)
                    item_list.append(iname + (f" (Área {area})" if area else ""))
            if item_list:
                lines.append(f"Itens coletáveis: {', '.join(item_list[:30])}")

        docs.append(Document(
            text="\n".join(lines),
            metadata={"source": "location", "name": name},
        ))
    return docs


# ============================================================
# ENTRY POINT
# ============================================================
def load_all_documents(progress_callback=None) -> list[Document]:
    """Carrega TODOS os dados do jogo como documentos estruturados."""
    def report(text: str):
        if progress_callback:
            progress_callback(text, 88)
        print(f"  📋 {text}")

    all_docs: list[Document] = []

    loaders = [
        ("Carregando monstros...", _load_monsters),
        ("Carregando armas...", _load_weapons),
        ("Carregando armaduras...", _load_armor),
        ("Carregando sets de armadura...", _load_armorsets),
        ("Carregando amuletos...", _load_charms),
        ("Carregando decorações...", _load_decorations),
        ("Carregando itens...", _load_items),
        ("Carregando skills...", _load_skills),
        ("Carregando quests...", _load_quests),
        ("Carregando kinsects...", _load_kinsects),
        ("Carregando ferramentas...", _load_tools),
        ("Carregando localizações...", _load_locations),
        ("Carregando conhecimento manual...", _load_manual_knowledge),
        ("Carregando catálogo de joias...", _load_jewel_catalog),
    ]

    for msg, loader_fn in loaders:
        report(msg)
        result = loader_fn()
        all_docs.extend(result)
        report(f"  → {len(result)} documentos")

    report(f"✅ Total: {len(all_docs)} documentos estruturados prontos para indexação")
    return all_docs
