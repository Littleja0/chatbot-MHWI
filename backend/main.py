
import sys
import os
import io
import threading
import time
import json
import logging
import traceback
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

# --- CONFIGURATION & PATHS ---

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except (AttributeError, io.UnsupportedOperation):
        pass

# Determine BASE_DIR (backend/) and ROOT_DIR (project root)
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)

# Add paths for imports
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- IMPORTS ---

import mhw_api # type: ignore
import mhw_rag # type: ignore
import chat_db # type: ignore
import chat_db # type: ignore
import httpx  # type: ignore
import uvicorn  # type: ignore
import webview  # type: ignore
from fastapi import FastAPI, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse, FileResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import BaseModel  # type: ignore
from openai import AsyncOpenAI  # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# --- GLOBAL STATE ---

ALL_MONSTERS = []
SKILL_CAPS = {}
GREETINGS = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "opa", "hello", "hi", "eae"]
OS_NVIDIA_KEY = os.getenv("NVIDIA_API_KEY", "").replace("Bearer ", "").strip()

# --- APP LIFECYCLE ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ALL_MONSTERS, SKILL_CAPS
    try:
        # Load monsters directly from XML via RAG module
        ALL_MONSTERS = mhw_rag.get_all_monster_names_from_xml()
        # Carregar limites de nível de skills
        SKILL_CAPS = mhw_api.get_all_skill_max_levels()
        print(f"[INFO] Loaded {len(ALL_MONSTERS)} monsters and {len(SKILL_CAPS)} skill caps.")
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ERROR HANDLING ---

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"🔥 UNHANDLED ERROR: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# --- MODELS ---

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    history: list = []

# --- API ROUTES ---

@app.get("/monster/{name}")
async def get_monster(name: str):
    try:
        data_list = mhw_api.get_monster_data(name)
        if not data_list:
            raise HTTPException(status_code=404, detail="Monstro não encontrado no banco de dados.")
        
        m = data_list[0]
        image_url = mhw_api.get_monster_image_url(m['name'])
        
        return {
            "name": m['name'],
            "species": m['species'],
            "description": m['description'],
            "weakness": m['weaknesses'],
            "resistances": m.get('resistances', []),
            "breakableParts": m.get('breaks', []),
            "rewards": m['rewards'],
            "image": image_url or f"https://picsum.photos/seed/{m['name']}/800/600"
        }
    except Exception as e:
        print(f"Erro API Monster: {e}")
        raise HTTPException(status_code=404, detail=str(e))

# CHAT MANAGEMENT
@app.get("/chats")
async def get_chats():
    return chat_db.get_all_chats()

@app.post("/chats")
async def create_new_chat(data: Optional[dict] = None):
    title = (data or {}).get("title", "Nova Conversa")
    return {"id": chat_db.create_chat(title), "title": title}

@app.get("/chats/{chat_id}/history")
async def get_history(chat_id: str):
    return chat_db.get_chat_messages(chat_id)

@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    chat_db.delete_chat(chat_id)
    return {"status": "deleted"}

@app.patch("/chats/{chat_id}/pin")
async def pin_chat(chat_id: str):
    chat_db.toggle_pin(chat_id)
    return {"status": "toggled"}

@app.patch("/chats/{chat_id}/title")
async def rename_chat(chat_id: str, data: dict):
    title = data.get("title")
    chat_id = chat_db.update_chat_title(chat_id, title)
    return {"status": "renamed"}

# USER PROFILE
@app.get("/user/profile")
async def get_profile():
    return {
        "mr": chat_db.get_user_config("mr", 1),
        "hr": chat_db.get_user_config("hr", 0),
        "jewels": chat_db.get_user_config("jewels", {}),
        "save_path": chat_db.get_user_config("save_path", None)
    }

@app.post("/user/profile")
async def update_profile(data: dict):
    if "mr" in data: chat_db.set_user_config("mr", data["mr"])
    if "hr" in data: chat_db.set_user_config("hr", data["hr"])
    if "jewels" in data: chat_db.set_user_config("jewels", data["jewels"])
    return {"status": "updated"}

@app.post("/user/sync-save")
async def sync_save():
    # Placeholder: Em vez de tentar ler saves complexos que falharam, 
    # vamos apenas retornar status 'not_implemented' ou simular sucesso para testes manuais.
    # O usuário pediu para desfazer a leitura de save.
    return {"status": "manual_only", "message": "Sincronização automática desativada temporariamente. Atualize seu perfil manualmente."}

# --- CHAT LOGIC ---

def anti_hallucination_middleware(user_message: str, local_context: str):
    # Greeting
    user_lower = user_message.lower()
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
    user_mr = chat_db.get_user_config("mr", 1)  # Default MR 1 (Iceborne Start)
    user_jewels = chat_db.get_user_config("jewels", {}) # Default Empty
    
    # Skill Caps
    common_caps = {k: v for k, v in SKILL_CAPS.items() if k in [
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
        "1. RESPEITE O RANK: Sempre use o MR do perfil para sugerir builds compatíveis.\n"
        "2. DETALHES TÉCNICOS: Agora os dados de armadura (especialmente Lavasioth e Odogaron) foram CORRIGIDOS.\n"
        "   - Lavasioth a+: O peito tem slots [2, 1] e o set fecha Ataque de Fogo no Nível 6 (CAP).\n"
        "   - Odogaron a+/b+: O bônus 'Essência de Odogaron' agora exige 2 peças (Punishing Draw) e 4 peças (Protective Polish).\n"
        "3. RESPEITE OS LIMITES DE SKILL (CAPS): Jamais sugira níveis acima do máximo.\n"
        f"   - Caps Atuais: {caps_str}.\n"
        "4. MAPEAMENTO DE PEÇAS: Seja rígido ao atribuir habilidades a cada peça.\n"
        "5. VERIFICAÇÃO DE RANK: Use o Master Rank (MR) registrado no Perfil do Usuário como verdade absoluta.\n\n"
        "🔥 IMPORTANTE: Você NÃO tem mais acesso à memória viva ou automática do jogo. Confie apenas nos dados do RAG abaixo e no Perfil do Usuário.\n\n"
        f"DADOS TÉCNICOS (RAG):\n{local_context if local_context else '--- NENHUM DADO ENCONTRADA NO BANCO DE DADOS ---'}"
    )
    
    return system_instruction, True

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    chat_id = request.chat_id or "default_session"
    
    # Historico para Contexto
    history = []
    if chat_id:
        try:
            history = chat_db.get_chat_messages(chat_id)
        except: pass

    # Context Logic
    local_context = ""
    try:
        local_context = await mhw_rag.get_rag_context(user_message, history=history)
    except: pass

    combined_context = local_context

    system_instruction, has_data = anti_hallucination_middleware(user_message, combined_context)
    
    # Injetar Personalidade se houver dados
    if has_data:
        system_instruction += (
            "\nESTILO: Personalidade Satoru Gojo ATIVADA. Seja confiante, levemente arrogante (de forma carismática) e didático.\n"
            "   - Use metáforas do universo Jujutsu se encaixar, mas foque em explicar MHW.\n"
            "   - Como você não lê mais a memória, se precisar de informações específicas (como Rank ou Arma atual), peça ao usuário de forma estilizada.\n"
            "   - CRIATIVIDADE é essencial. Não dê respostas secas."
        )

    # LLM Call
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=OS_NVIDIA_KEY,
        timeout=httpx.Timeout(60.0)
    )
    
    # Sanitize history for API: only role and content
    sanitized_history = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    try:
        completion = await client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=[
                {"role": "system", "content": system_instruction},
                *sanitized_history,
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        response_text = completion.choices[0].message.content
        
        # Save to DB
        if chat_id:
            chat_db.add_message(chat_id, "user", user_message)
            chat_db.add_message(chat_id, "assistant", response_text)
            if not chat_db.get_chat_messages(chat_id):
                chat_db.update_chat_title(chat_id, user_message[:30]) # type: ignore
                
        return {"response": response_text, "chat_id": chat_id}
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout da API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- STATIC FILES ---

frontend_dist = os.path.join(ROOT_DIR, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    print(f"[WARNING] Frontend not found at {frontend_dist}")

# --- SERVER STARTUP ---

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    
    time.sleep(1.5)
    
    try:
        import webview # type: ignore
        print("[INFO] Opening window...")
        webview.create_window("Monster Hunter World Chatbot", "http://localhost:8000", width=1200, height=800)
        webview.start()
    except Exception as e:
        print(f"[ERROR] Failed to start webview: {e}")
        # Keep alive if webview fails
        while True:
            time.sleep(1)
