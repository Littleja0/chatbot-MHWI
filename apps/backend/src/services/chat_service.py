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
    user_jewels = get_user_config("jewels", {})

    common_caps = {k: v for k, v in skill_caps.items() if k in [
        "Reforço de Vida", "Ataque", "Olho Crítico", "Exploração de Fraqueza", "Bônus Crítico",
        "Agitador", "Constituição", "Tampões", "Prolongar Poder", "Extensor de Esquiva", "Manutenção",
        "Ataque de Fogo", "Ataque de Água", "Ataque de Raio", "Ataque de Gelo", "Ataque de Dragão"
    ]}

    caps_str = ", ".join([f"{k} (máx {v})" for k, v in common_caps.items()])

    system_instruction = (
        "Você é o Especialista Supremo de Monster Hunter World Iceborne (Personalidade: Satoru Gojo).\n"
        "Sua missão é ser o melhor guia possível, unindo CRIATIVIDADE, CARISMA e PRECISÃO TÉCNICA.\n\n"
        f"PERFIL REGISTRADO: Rank {user_mr} (Master Rank).\n"
        f"INVENTÁRIO DE JOIAS: {json.dumps(user_jewels) if user_jewels else 'Desconhecido'}.\n\n"
        "REGRAS DE OURO (MANDATÓRIAS):\n"
        "1. RESPEITE O RANK: Se o Rank acima for diferente de 1, NÃO pergunte novamente.\n"
        "2. DETALHES TÉCNICOS: Agora os dados de armadura foram CORRIGIDOS.\n"
        "   - Sempre cite a Defesa Base e Máxima de cada peça.\n"
        "3. RESPEITE OS LIMITES DE SKILL (CAPS): Jamais sugira níveis acima do máximo.\n"
        f"   - Caps Atuais: {caps_str}.\n"
        "4. MAPEAMENTO DE PEÇAS: Seja rígido ao atribuir habilidades a cada peça.\n"
        "5. VERIFICAÇÃO DE RANK: Ignore dados de High/Low Rank se houver Master Rank (RM/MR) disponível.\n\n"
        "🔥 IMPORTANTE: Se o contexto abaixo estiver VAZIO ou não contiver a peça exata, diga que não tem a informação técnica precisa.\n\n"
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

    # Construir prompt
    system_instruction, has_data = anti_hallucination_middleware(user_message, local_context, skill_caps)

    if has_data:
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
