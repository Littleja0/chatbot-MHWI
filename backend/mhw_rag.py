"""
mhw_rag.py — Motor de RAG do MHW Chatbot.

Melhorias implementadas:
- Detecção automática de mudanças nos XMLs (via rag_pipeline)
- Rebuild automático quando XMLs são alterados (sem deletar storage manualmente)
- Multi-query expansion para melhorar recall
- Hot-reload do query engine sem reiniciar o servidor
"""

import os
import re
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings  # type: ignore
from llama_index.llms.nvidia import NVIDIA  # type: ignore
from llama_index.embeddings.nvidia import NVIDIAEmbedding  # type: ignore
from typing import List, Any, Optional, Union

from dotenv import load_dotenv  # type: ignore

# Localizar .env na raiz do projeto
import sys
if getattr(sys, 'frozen', False):
    # No PyInstaller, o .env costuma ser colocado na raiz do _MEIPASS
    ROOT_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Configurações do NVIDIA AI Foundation
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "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")
if not NVIDIA_API_KEY:
    NVIDIA_API_KEY = "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"

# Limpar Bearer se houver
NVIDIA_API_KEY = NVIDIA_API_KEY.replace("Bearer ", "").strip()
os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY

# Configurar o LlamaIndex para usar NVIDIA
Settings.llm = NVIDIA(model="moonshotai/kimi-k2-instruct-0905")
Settings.embed_model = NVIDIAEmbedding(model="nvidia/nv-embedqa-e5-v5", truncate="END")

# Caminhos
RAG_PATH = Path("rag")
STORAGE_PATH = Path("storage")

# Instância global do motor
_query_engine = None


def setup_rag_engine(progress_callback=None):
    """
    Inicializa o motor de RAG com detecção inteligente de mudanças.
    
    Fluxo:
    1. Se storage existe E nenhum XML mudou → carrega do cache (rápido)
    2. Se storage não existe OU XMLs mudaram → rebuild completo
    3. Após rebuild, salva manifesto para próxima comparação
    """
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    import threading
    import rag_pipeline  # type: ignore

    def report(text, progress=None):
        if progress is None:
            progress = 50
        if progress_callback:
            progress_callback(text, progress)
        print(f"  📋 {text}")

    def run_with_heartbeat(task_fn, base_msg, start_pct, end_pct, interval=2.0):
        """
        Executa task_fn em thread separada e envia heartbeats periódicos
        para o callback de progresso, evitando que o usuário pense que travou.
        """
        result: List[Optional[Any]] = [None]
        error: List[Optional[Exception]] = [None]
        done = threading.Event()

        def worker():
            try:
                result[0] = task_fn()
            except Exception as e:
                error[0] = e
            finally:
                done.set()

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        elapsed: float = 0.0
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        while not done.is_set():
            done.wait(interval)
            if not done.is_set():
                elapsed = elapsed + interval  # type: ignore
                frac = min(elapsed / 30.0, 0.9)
                pct = int(start_pct + frac * (end_pct - start_pct))
                dot = dots[int(elapsed / interval) % len(dots)]
                report(f"{dot} {base_msg} ({int(elapsed)}s)", pct)

        t.join()
        err = error[0]
        if err is not None:
            raise err
        return result[0]

    if not RAG_PATH.exists():
        report("Erro: Pasta 'rag' não encontrada!", 100)
        return None

    # === DECISÃO INTELIGENTE: Carregar ou Reconstruir? ===
    should_rebuild = rag_pipeline.needs_rebuild()

    if not should_rebuild:
        # FAST PATH: XMLs não mudaram, carregar do cache
        total_mb = sum(
            f.stat().st_size for f in STORAGE_PATH.iterdir() if f.is_file()
        ) / (1024 * 1024)
        report(f"📂 Carregando base de dados ({total_mb:.0f} MB)...", 85)

        def load_storage():
            ctx = StorageContext.from_defaults(persist_dir=str(STORAGE_PATH))
            return load_index_from_storage(ctx)

        index = run_with_heartbeat(
            load_storage,
            "Carregando vetores e índices",
            86, 97,
            interval=2.0
        )

        report("✅ Base de dados carregada! (nenhum XML modificado)", 97)
    else:
        # REBUILD: XMLs mudaram ou primeira execução
        report("🔨 Construindo base de conhecimento (XMLs alterados detectados)...", 80)

        # Limpar storage antigo se existir
        if STORAGE_PATH.exists():
            import shutil
            shutil.rmtree(STORAGE_PATH, ignore_errors=True)
            report("🗑️ Storage antigo removido (XMLs alterados)", 81)

        # Usar o loader inteligente que parseia XMLs em documentos estruturados
        from rag_loader import load_all_documents  # type: ignore

        report("📋 Parseando dados do jogo...", 82)
        documents = load_all_documents(progress_callback=progress_callback)

        report(f"📊 Gerando índice ({len(documents)} documentos estruturados)...", 90)

        def build_index():
            return VectorStoreIndex.from_documents(documents, show_progress=True)

        index = run_with_heartbeat(
            build_index,
            "Gerando embeddings",
            90, 96,
            interval=3.0
        )

        report("💾 Salvando base de dados para uso futuro...", 97)
        STORAGE_PATH.mkdir(exist_ok=True)
        if index is not None:
            index.storage_context.persist(persist_dir=str(STORAGE_PATH))

        # Salvar manifesto com hashes dos XMLs atuais
        rag_pipeline.save_manifest()
        report("✅ Base de dados pronta! Manifesto salvo.", 98)

    report("⚔️ Preparando assistente...", 99)
    if index is not None:
        _query_engine = index.as_query_engine(similarity_top_k=30)
    return _query_engine


# ============================================================
# MULTI-QUERY EXPANSION — Melhora o recall
# ============================================================

# Mapeamento de nomes completos → abreviações usadas nas armaduras/armas
MONSTER_ABBREVIATIONS = {
    "beotodus": "Beo", "great jagras": "Jagras",
    "kulu-ya-ku": "Kulu", "pukei-pukei": "Pukei",
    "jyuratodus": "Jyura", "tobi-kadachi": "Kadachi",
    "anjanath": "Anja", "barroth": "Barroth",
    "radobaan": "Radobaan", "legiana": "Legi",
    "odogaron": "Odo", "rathalos": "Rath",
    "rathian": "Rathian", "diablos": "Diablos",
    "dodogama": "Dodo", "lavasioth": "Lava",
    "uragaan": "Uragaan", "deviljho": "Jho",
    "bazelgeuse": "Bazel", "paolumu": "Paol",
    "tzitzi-ya-ku": "Tzitzi", "great girros": "Girros",
    "nergigante": "Nerg", "teostra": "Teostra",
    "lunastra": "Luna", "kushala daora": "Kushala",
    "vaal hazak": "Vaal", "kirin": "Kirin",
    "xeno'jiiva": "Xeno", "kulve taroth": "Kulve",
    "behemoth": "Behemoth", "leshen": "Leshen",
    "zinogre": "Zinogre", "brachydios": "Brachy",
    "glavenus": "Glavenus", "tigrex": "Tigrex",
    "banbaro": "Banbaro", "nargacuga": "Narga",
    "barioth": "Barioth", "velkhana": "Velkhana",
    "namielle": "Namielle", "rajang": "Rajang",
    "shara ishvalda": "Shara", "safi'jiiva": "Safi",
    "alatreon": "Alatreon", "fatalis": "Fatalis",
    "stygian zinogre": "Stygian Zinogre",
    "raging brachydios": "Raging Brachy",
    "furious rajang": "Furious Rajang",
    "ruiner nergigante": "Ruiner Nerg",
    "gold rathian": "Gold Rathian",
    "silver rathalos": "Silver Rath",
    "fulgur anjanath": "Fulgur Anja",
    "ebony odogaron": "Ebony Odo",
    "acidic glavenus": "Acidic Glav",
    "shrieking legiana": "Shrieking Legi",
    "coral pukei-pukei": "Coral Pukei",
    "viper tobi-kadachi": "Viper Kadachi",
    "nightshade paolumu": "Nightshade Paol",
    "yian garuga": "Garuga",
    "scarred yian garuga": "Scarred Garuga",
    "seething bazelgeuse": "Seething Bazel",
    "blackveil vaal hazak": "Blackveil Vaal",
}


def _expand_queries(prompt: str, history_text: str = "") -> list[str]:
    """
    Expande o prompt do usuário em múltiplas sub-queries para melhorar o recall.
    Lida com abreviações de armaduras/armas e conversões α/β/γ.
    Usa history_text para pegar o monstro do contexto anterior se o prompt for vago.
    """
    queries = [prompt]
    lower = prompt.lower()
    full_search_text = (lower + " " + history_text.lower()).strip()

    # Detectar nomes de monstros — processa os mais longos primeiro (evita match parcial)
    for monster_name, abbrev in sorted(
        MONSTER_ABBREVIATIONS.items(), key=lambda x: len(x[0]), reverse=True
    ):
        if monster_name in full_search_text:
            # Se o monstro está no prompt atual, damos prioridade. 
            # Se está só no histórico, só usamos se o prompt atual for "vago" (não tem monstro)
            if monster_name not in lower and any(m in lower for m in MONSTER_ABBREVIATIONS.keys()):
                continue

            is_armor = "armadura" in lower or "armor" in lower or "set" in lower or "peça" in lower
            is_weapon = (
                "arma " in lower or "weapon" in lower or "espada" in lower
                or lower.startswith("arma") or "sword" in lower or "hammer" in lower
            )
            is_craft = (
                "craft" in lower or "material" in lower or "preciso" in lower
                or "fazer" in lower or "criar" in lower or "montar" in lower
            )

            if is_armor:
                queries.append(f"CONJUNTO DE ARMADURA: {monster_name}")
                queries.append(f"CONJUNTO DE ARMADURA: {abbrev}")
                queries.append(f"ARMADURA: {monster_name}")
                queries.append(f"ARMADURA: {abbrev}")
                queries.append(f"SET: {monster_name}")
            if is_weapon and not is_armor:
                queries.append(f"ARMA: {monster_name}")
                queries.append(f"ARMA: {abbrev}")
            if is_craft or is_armor:
                queries.append(f"Materiais {monster_name}")
                queries.append(f"Materiais {abbrev}")
            if "fraqueza" in lower or "weakness" in lower:
                queries.append(f"MONSTRO: {monster_name} fraquezas elementais")
            # Sempre buscar o monstro base
            queries.append(f"MONSTRO: {monster_name}")
            break

    # Conversões de símbolos gregos (agora preservando o contexto do set)
    alpha_beta = {
        "a+": "α+", "alpha+": "α+", "alpha +": "α+",
        "b+": "β+", "beta+": "β+", "beta +": "β+",
        "g+": "γ+", "gamma+": "γ+", "gamma +": "γ+",
    }
    for term, replacement in alpha_beta.items():
        if term in lower:
            fixed_term = prompt.lower().replace(term, replacement)
            queries.append(fixed_term)
            if "armadura" in lower or "set" in lower:
                # Se falou em set e alpha/beta, tenta buscar o conjunto com o símbolo correto
                for monster_name in MONSTER_ABBREVIATIONS.keys():
                    if monster_name in lower:
                        queries.append(f"CONJUNTO DE ARMADURA: {monster_name} {replacement}")

    # Detecção de Elemento para Builds
    if "gelo" in lower or "ice" in lower:
        queries.append("CONJUNTO DE ARMADURA: Barioth")
        queries.append("CONJUNTO DE ARMADURA: Beotodus")
        queries.append("CONJUNTO DE ARMADURA: Velkhana")
        queries.append("Armas de Gelo recomendadas")
    if "fogo" in lower or "fire" in lower:
        queries.append("CONJUNTO DE ARMADURA: Rathalos")
        queries.append("CONJUNTO DE ARMADURA: Anjanath")
        queries.append("CONJUNTO DE ARMADURA: Teostra")
    if "trovão" in lower or "thunder" in lower or "raio" in lower:
        queries.append("CONJUNTO DE ARMADURA: Zinogre")
        queries.append("CONJUNTO DE ARMADURA: Tobi-Kadachi")
        queries.append("CONJUNTO DE ARMADURA: Fulgur Anja")

    # Detecção de Rank/Raridade nas queries
    is_mr = "mr " in lower or " rm" in lower or "rank m" in lower or lower.endswith(" mr") or lower.endswith(" rm")
    if is_mr:
        queries.append("CONJUNTO DE ARMADURA: Master Rank (MR)")
        queries.append("CONJUNTO DE ARMADURA: RM")
    
    if "rank" in lower:
         queries.append("Master Rank (MR)")

    if "r9" in lower or "raridade 9" in lower:
        queries.append("Raridade 9")
    if "r10" in lower or "raridade 10" in lower:
        queries.append("Raridade 10")

    # Keywords de sets comuns (não vinculados a monstros)
    common_sets = {
        "óssea": ["Óssea", "Bone"],
        "bone": ["Bone", "Óssea"],
        "osso": ["Osso", "Bone"],
        "liga": ["Liga Leve", "Alloy"],
        "alloy": ["Alloy", "Liga Leve"],
        "couro": ["Couro", "Leather"],
        "leather": ["Leather", "Couro"],
        "metal": ["Metal", "Alloy", "Liga Leve"],
    }
    for kw, targets in common_sets.items():
        if kw in lower:
            for t in targets:
                queries.append(f"CONJUNTO DE ARMADURA: {t}")
                if is_mr:
                    queries.append(f"CONJUNTO DE ARMADURA: {t} α+")
                    queries.append(f"CONJUNTO DE ARMADURA: {t} β+")

    return list(dict.fromkeys(queries))  # Deduplica mantendo ordem


async def get_rag_context(prompt: str, history: Optional[List[dict]] = None) -> str:
    """
    Recupera contexto relevante usando multi-query expansion de forma ASSÍNCRONA.
    Faz múltiplas buscas paralelas no índice para maximizar o recall e performance.
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = setup_rag_engine()

    if not _query_engine:
        return ""

    import asyncio
    retriever = _query_engine._retriever

    # Extrair texto do histórico para contexto (últimas 2 mensagens do usuário)
    history_text = ""
    if history:
        user_msgs: List[str] = [m["content"] for m in history if m["role"] == "user"]
        history_text = " ".join(user_msgs[-2:]) if user_msgs else "" # type: ignore

    # Expandir prompt em múltiplas queries usando também o histórico
    queries = _expand_queries(prompt, history_text)

    # Coletar todos os nodes únicos de todas as queries em paralelo
    async def retrieve_task(q):
        try:
            # Tentar versão assíncrona do retriever (LlamaIndex)
            if hasattr(retriever, "aretrieve"):
                return await retriever.aretrieve(q)
            else:
                return retriever.retrieve(q)
        except Exception as e:
            print(f"  ⚠️ Erro na query '{q[:50]}': {e}")
            return []

    # Disparar todas as buscas ao mesmo tempo
    from typing import cast
    tasks = [retrieve_task(q) for q in queries]
    results = cast(List[Any], await asyncio.gather(*tasks))

    # Deduplicar e juntar conteúdos
    seen_keys: set = set()
    all_contents: list = []

    for nodes in results:
        for node in nodes:
            content = node.get_content()
            # Deduplica por início do conteúdo (expandido para 400 chars para evitar falsos positivos em headers similares)
            key = content[:400]
            if key not in seen_keys:
                seen_keys.add(key)
                all_contents.append(content)

    return "\n\n".join(all_contents)


def get_all_monster_names_from_xml() -> list[str]:
    """
    Extrai todos os nomes de monstros do arquivo monster_text.xml (PT e EN).
    """
    import xml.etree.ElementTree as ET

    monster_text_path = RAG_PATH / "monster_text.xml"
    if not monster_text_path.exists():
        return []

    names: set = set()
    try:
        tree = ET.parse(monster_text_path)
        root = tree.getroot()
        for record in root.findall("DATA_RECORD"):
            lang = record.find("lang_id")
            name = record.find("name")
            if lang is not None and lang.text in ["pt", "en"] and name is not None and name.text:
                names.add(name.text)
    except Exception as e:
        print(f"Erro ao extrair nomes do XML: {e}")

    return list(names)


def get_rag_response(prompt: str) -> str:
    """
    Busca a resposta utilizando o motor de RAG.
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = setup_rag_engine()

    if _query_engine:
        response = _query_engine.query(prompt)
        return str(response)
    return "Erro ao inicializar o motor de RAG."


def reload_engine():
    """
    Força reconstrução do índice (hot-reload).
    Chamado pelo rag_pipeline quando detecta mudanças.
    """
    global _query_engine
    _query_engine = None
    return setup_rag_engine()


if __name__ == "__main__":
    # Teste rápido
    print("Iniciando teste do RAG...")
    query = "Quais são as fraquezas do Rathalos e seus drops principais?"
    print(f"Pergunta: {query}")
    print(f"Resposta: {get_rag_response(query)}")
