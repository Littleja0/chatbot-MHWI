"""
chat_service.py — Lógica de negócio do Chat.

Contém o middleware anti-alucinação, construção do prompt do sistema,
e orquestração da chamada à LLM.
"""

import re
import json
from typing import Optional, List

import httpx  # type: ignore
from openai import AsyncOpenAI  # type: ignore

from core.config import NVIDIA_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT, LLM_TEMPERATURE, LLM_MAX_TOKENS, GREETINGS
from data.db import get_user_config, set_user_config, add_message, get_chat_messages, update_chat_title
from core.mhw.mhw_tools import get_armor_details, get_weapon_details


# --- Anti-Hallucination Middleware ---

def anti_hallucination_middleware(
    user_message: str,
    local_context: str,
    skill_caps: dict
) -> tuple[str, bool]:
    """
    Analisa a mensagem do usuário e retorna a instrução do sistema + flag de dados.

    Returns:
        (system_instruction, has_data)
    """
    user_lower = user_message.lower()

    # Greeting
    is_greeting = any(g in user_lower for g in GREETINGS) and len(user_lower.split()) < 4
    if is_greeting:
        return (
            "Você é o Especialista Supremo de Monster Hunter World Iceborne, com a personalidade do Satoru Gojo. "
            "O usuário está apenas te cumprimentando. Responda de forma curta e amigável."
        ), True

    # No Data
    db_found = len(local_context.strip()) > 100
    if not db_found:
        return (
            "EXTREMA PRIORIDADE: O usuário pediu algo sem dados suficientes no RAG. "
            "Você é um assistente de RAG e tem PROIBIÇÃO TOTAL de inventar skills ou equipamentos. "
            "Responda apenas que não possui dados exatos o suficiente para montar essa build com segurança."
        ), False

    # Build Logic
    user_mr = get_user_config("mr", 1)

    common_caps = {k: v for k, v in skill_caps.items() if k in [
        "Reforço de Vida", "Ataque", "Olho Crítico", "Exploração de Fraqueza", "Bônus Crítico",
        "Agitador", "Constituição", "Tampões", "Prolongar Poder", "Extensor de Esquiva", "Manutenção",
        "Ataque de Fogo", "Ataque de Água", "Ataque de Raio", "Ataque de Gelo", "Ataque de Dragão"
    ]}

    caps_str = ", ".join([f"{k} (máx {v})" for k, v in common_caps.items()])

    system_instruction = (
        "Você é o Especialista Supremo de Monster Hunter World Iceborne (Personalidade: Satoru Gojo).\n"
        "Sua missão é ser o melhor guia possível, unindo CRIATIVIDADE, CARISMA e PRECISÃO TÉCNICA.\n\n"
        f"PERFIL REGISTRADO: Rank {user_mr} (Master Rank).\n\n"
        "REGRAS DE OURO (MANDATÓRIAS):\n"
        "1. RESPEITE O RANK: Se o Rank acima for diferente de 1, NÃO pergunte novamente.\n"
        "2. DETALHES TÉCNICOS EM TABELA: Toda vez que o usuário pedir uma BUILD, COMPARATIVO ou LISTA DE ARMAS, você DEVE fornecer o resultado principal em formato de TABELA Markdown.\n"
        "3. PROIBIÇÃO DE INVENÇÃO: Use APENAS os dados da seção 'DADOS TÉCNICOS VERIFICADOS (SQL)'.\n"
        "   - Se a seção SQL não listar uma peça que você quer recomendar, VOCÊ É OBRIGADO a dizer: 'Eu não tenho os dados técnicos de slots/skills verificados para a peça [Nome], por isso não posso recomendá-la com precisão agora'.\n"
        "   - NÃO INVENTE SLOTS. Se o SQL diz [4], é apenas um slot de nível 4. Se o SQL diz [4, 1], são dois slots.\n"
        "4. MESTRE DAS ÁRVORES: Você sabe que armas de variantes (ex: Shrieking Legiana ou Stygian Zinogre) fazem parte da árvore principal. Se o usuário pedir 'Katanas da Legiana', você deve mostrar também a 'Ladra Glacial' e 'Glácia de Apsará' se aparecerem no SQL.\n"
        "5. NOMES EM PORTUGUÊS: Use SEMPRE os nomes traduzidos (Ex: 'Larápia de Legia+', 'Geadefesa', 'Velkhana').\n"
        "6. VERIFIQUE O TIPO: Jamais recomende um Espadão (Great Sword) quando o usuário pedir uma Katana (Long Sword).\n"
        "7. BUSCA PROATIVA: Se você não encontrar uma arma pelo nome do monstro, use a ferramenta `search_equipment` com o elemento e tipo de arma para ver TODAS as opções.\n\n"
        "🔥 IMPORTANTE: O bloco 'DADOS TÉCNICOS VERIFICADOS (SQL)' é a sua ÚNICA FONTE DE VERDADE. Se ele estiver vazio para o que você quer sugerir, admita que não sabe os dados exatos daquela peça.\n\n"
        "{sql_verified_data}" # Placeholder para injeção posterior
        f"DADOS TÉCNICOS (RAG):\n{local_context if local_context else '--- NENHUM DADO ENCONTRADO NO BANCO DE DADOS ---'}"
    )

    return system_instruction, True


def _inject_personality(system_instruction: str) -> str:
    """Injeta personalidade do Gojo no prompt do sistema."""
    return system_instruction + (
        "\nESTILO: Personalidade Satoru Gojo ATIVADA. Seja confiante, levemente arrogante (de forma carismática) e didático.\n"
        "   - Use metáforas do universo Jujutsu se encaixar, mas foque em explicar MHW.\n"
        "   - Se faltar informação (como o Rank), provoque o usuário.\n"
        "   - CRIATIVIDADE é essencial. Não dê respostas secas."
    )


def _auto_detect_mr(user_message: str):
    """Auto-detecta MR na mensagem e atualiza perfil."""
    mr_match = re.search(r'(?:mr|rm|rank|master rank)\s*(\d+)', user_message.lower())
    if mr_match:
        try:
            new_mr = int(mr_match.group(1))
            set_user_config("mr", new_mr)
        except (ValueError, TypeError):
            pass

def _extract_and_verify_equipment(context: str, user_query: str = "") -> str:
    """Extrai nomes de equipamentos do contexto RAG e da query do usuário para busca SQL."""
    # 1. Extração do contexto RAG
    armor_pieces = re.findall(r'> PEÇA:\s*(.*?)\s*\(', context)
    armor_sets = re.findall(r'===\s*(?:SET|CONJUNTO) DE ARMADURA:\s*(.*?)\s*(?:===|\[)', context)
    weapons = re.findall(r'===\s*ARMA:\s*(.*?)\s*\(', context)
    
    if not armor_pieces:
        armor_pieces = re.findall(r'> PEÇA:\s*(.*?)$', context, re.MULTILINE)

    # 1.5. Extração da query do usuário (Build Exportada)
    # Padrão: "Cintura: Nome da Peça [Skills]" ou "Elmo: Nome"
    user_pieces = re.findall(r'(?:Elmo|Peito|Braços|Cintura|Pernas|Waist|Head|Chest|Arms|Legs):\s*(.*?)(?:\s*\[|$)', user_query)
    user_weapons = re.findall(r'Arma:\s*(.*?)(?:\r?\n|$)', user_query, re.IGNORECASE)

    # 2. Busca Proativa baseada na mensagem do usuário
    from core.mhw.mhw_tools import MONSTER_TREE_MAP, MONSTER_EQUIPMENT_MAP, ELEMENT_MAP, WEAPON_MAP, search_equipment
    
    query_lower = user_query.lower()
    proactive_search_terms = []
    
    # Detecção de Monstros
    for monster in MONSTER_TREE_MAP.keys():
        if monster in query_lower:
            proactive_search_terms.append(monster)
            
    # Detecção de Elemento e Tipo de Arma para busca global
    detected_element = None
    for k, v in ELEMENT_MAP.items():
        if k in query_lower:
            detected_element = v
            break
            
    detected_type = None
    for k, v in WEAPON_MAP.items():
        if k in query_lower:
            detected_type = v
            break
    
    verified_entries = []
    seen_names = set()

    # Se detectou Elemento + Tipo, faz busca proativa global
    if detected_element and detected_type:
        proactive_results_json = search_equipment(element=detected_element, piece_type=detected_type, category="weapon")
        if proactive_results_json and not proactive_results_json.startswith("Nenhum"):
            try:
                proactive_results = json.loads(proactive_results_json)
                for res in proactive_results:
                    name = res["name_pt"]
                    if name not in seen_names:
                        slots_str = f"Slots: {res['slots']}" if res['slots'] else "Sem slots"
                        stats_str = f"Ataque: {res['attack']} | Afinidade: {res['affinity']} | Elemento: {res['element']}"
                        monstro_str = f" | Monstro: {res['monstro']}" if res.get("monstro") else ""
                        verified_entries.append(f"ARMA: {res['name_pt']} ({res['name_en']}) | TIPO: {res['type_pt']} ({res['type_en']}){monstro_str} | {stats_str} | {slots_str}")
                        seen_names.add(name)
            except:
                pass

    # Combinamos tudo para verificar outros itens citados ou encontrados via RAG
    search_list = list(dict.fromkeys(armor_sets + armor_pieces + user_pieces + proactive_search_terms))

    # Processar Armaduras
    for name in search_list:
        if name in seen_names: continue
        details = get_armor_details(name)
        if details:
            skills_str = ", ".join([f"{s['name']} Lv{s['points']}" for s in details['skills']])
            slots_str = f"Slots: {details['slots']}" if details['slots'] else "Sem slots"
            verified_entries.append(f"ARMADURA: {details['name']} -> {skills_str} | {slots_str}")
            seen_names.add(name)

    # Processar Armas encontradas no RAG ou Termos Proativos ou Query
    weapon_search_list = list(dict.fromkeys(weapons + user_weapons + proactive_search_terms))
    for name in weapon_search_list:
        if name in seen_names: continue
        details = get_weapon_details(name)
        if details:
            slots_str = f"Slots: {details['slots']}" if details['slots'] else "Sem slots"
            stats_str = f"Ataque: {details['attack']} | Afinidade: {details['affinity']} | Elemento: {details['element']}"
            monstro_str = f" | Monstro: {details['monstro']}" if details.get("monstro") else ""
            verified_entries.append(f"ARMA: {details['name_pt']} ({details['name_en']}) | TIPO: {details['type_pt']} ({details['type_en']}){monstro_str} | {stats_str} | {slots_str}")
            seen_names.add(name)

    if not verified_entries:
        return ""

    return "\n[!!!] DADOS TÉCNICOS VERIFICADOS (SQL - FONTE DE VERDADE ABSOLUTA) [!!!]\n" + "\n".join(verified_entries) + "\n--------------------------------------------------------------\n"


async def process_chat(
    user_message: str,
    chat_id: str,
    skill_caps: dict,
    get_rag_context_fn,
) -> dict:
    """
    Processa uma mensagem de chat completa.

    Args:
        user_message: Mensagem do usuário.
        chat_id: ID do chat.
        skill_caps: Limites de nível de skills.
        get_rag_context_fn: Função assíncrona para obter contexto RAG.

    Returns:
        {"response": str, "chat_id": str}
    """
    # Carregar histórico
    history = []
    try:
        history = get_chat_messages(chat_id)
    except Exception:
        pass

    # Obter contexto RAG
    local_context = ""
    try:
        local_context = await get_rag_context_fn(user_message, history=history)
    except Exception:
        pass

    # Auto-update MR
    _auto_detect_mr(user_message)

    # 9.5: Detect exported build data from Builder
    is_build_export = "📋 BUILD EXPORTADA" in user_message or "===[ BUILD EXPORTADA ]===" in user_message

    if is_build_export:
        # Build export detected — inject specialized analysis prompt
        system_instruction = (
            "Você é o Especialista Supremo de Monster Hunter World Iceborne (Personalidade: Satoru Gojo).\n"
            "O usuário acabou de exportar uma BUILD do Builder interativo para você analisar.\n\n"
            "INSTRUÇÕES PARA ANÁLISE DA BUILD:\n"
            "1. LEIA com atenção todos os detalhes da build (arma, armaduras, joias, skills ativas, EFR).\n"
            "2. ANALISE os pontos fortes e fracos da build.\n"
            "3. VERIFIQUE se as skills fazem sentido para o tipo de arma escolhida.\n"
            "4. SUGIRA melhorias concretas (troca de peças, joias alternativas, skills faltantes).\n"
            "5. AVALIE o EFR — compare com referências típicas para o tipo de arma.\n"
            "6. COMENTE sobre set bonuses ativos e se valem a pena.\n"
            "7. DÊ UMA NOTA de 1 a 10 para a build, justificando.\n\n"
            "FORMATO DE RESPOSTA:\n"
            "- Use tabelas Markdown quando apropriado\n"
            "- Seja detalhado mas direto\n"
            "- Use a personalidade do Gojo (confiante, carismático)\n"
            "- Se a build for boa, elogie com empolgação\n"
            "- Se tiver problemas, aponte com respeito mas firmeza\n\n"
            "🔥 IMPORTANTE: O bloco 'DADOS TÉCNICOS VERIFICADOS (SQL)' é a sua ÚNICA FONTE DE VERDADE para slots e raridades.\n"
            "NÃO INVENTE JOIAS. Se o SQL diz que a peça tem slots [4, 1], você não pode sugerir uma joia de nível 2 se não houver um slot compatível.\n"
            "NÃO EXISTE 'Joia Ataque 2'. Joias de Ataque são nível 1 (Joia Ataque 1) ou nível 4 (Joia Ataque+ 4).\n\n"
            "{sql_verified_data}"
        )
        system_instruction = _inject_personality(system_instruction)
        has_data = True
    else:
        # Normal flow
        # Construir prompt
        system_instruction, has_data = anti_hallucination_middleware(user_message, local_context, skill_caps)

    if has_data:
        # Enriquecimento com SQL (passando a query do usuário para busca proativa)
        sql_verified_data = _extract_and_verify_equipment(local_context, user_message)
        # Substitui o placeholder ou limpa se estiver vazio
        if sql_verified_data:
            system_instruction = system_instruction.replace("{sql_verified_data}", sql_verified_data + "\n")
        else:
            system_instruction = system_instruction.replace("{sql_verified_data}", "")
        
        system_instruction = _inject_personality(system_instruction)

    # LLM Call
    client = AsyncOpenAI(
        base_url=LLM_BASE_URL,
        api_key=NVIDIA_API_KEY,
        timeout=httpx.Timeout(LLM_TIMEOUT)
    )

    sanitized_history = [{"role": msg["role"], "content": msg["content"]} for msg in history]

    try:
        completion = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                *sanitized_history,
                {"role": "user", "content": user_message}
            ],
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        response_text = completion.choices[0].message.content

        # Save to DB
        if chat_id:
            add_message(chat_id, "user", user_message)
            add_message(chat_id, "assistant", response_text)
            if not get_chat_messages(chat_id):
                update_chat_title(chat_id, user_message[:30])

        return {"response": response_text, "chat_id": chat_id}

    except httpx.TimeoutException:
        raise TimeoutError("Timeout da API.")
    except Exception as e:
        raise RuntimeError(str(e))
