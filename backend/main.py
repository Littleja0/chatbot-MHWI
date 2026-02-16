import sys
import os
import io
from pathlib import Path

# Forçar UTF-8 no stdout/stderr para evitar erro de charmap com emojis no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
    except (AttributeError, io.UnsupportedOperation):
        pass

# Ajustar sys.path para encontrar módulos tanto em dev quanto no executável
if getattr(sys, 'frozen', False):
    # No PyInstaller, todos os arquivos .py ficam na raiz temporária (_MEIPASS)
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ROOT_DIR = BASE_DIR
else:
    # Em desenvolvimento, a pasta de trabalho é a /backend
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)

# Adicionar ambos ao path para garantir que mhw_rag (em /backend) e updater (na raiz) sejam encontrados
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Agora os imports funcionam independente do local
import mhw_api # type: ignore
import mhw_rag # type: ignore
import rag_pipeline # type: ignore
import updater # type: ignore
from typing import List, Any, Optional, Union, cast
import chat_db # type: ignore
import json
import asyncio
import httpx  # type: ignore
import uvicorn  # type: ignore
import webview  # type: ignore
import threading
import time
import logging

# Configuração de Logs para a Splash
class SplashLogHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        msg = self.format(record)
        if self.callback:
            # Tenta extrair progresso se houver algo no texto ou mantém o atual
            self.callback(msg, None)

class SplashStdout:
    def __init__(self, callback, original):
        self.callback = callback
        self.original = original

    def write(self, s):
        try:
            self.original.write(s)
        except Exception:
            # Se falhar ao escrever no console real, ignoramos o erro
            # O importante é que o callback (UI) continue funcionando
            pass
            
        if s.strip() and self.callback:
            # Evita loops infinitos e mensagens muito curtas
            clean_s = s.strip()
            if len(clean_s) > 2:
                # O webview aceita unicode normalmente via JSON
                self.callback(clean_s, None)

    def flush(self):
        self.original.flush()

from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import BaseModel  # type: ignore
from openai import AsyncOpenAI  # type: ignore
from contextlib import asynccontextmanager

# Cache monster names for entity extraction
ALL_MONSTERS = []

# Lista unificada de saudações para evitar inconsistências
GREETINGS = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "opa", "hello", "hi", "eae"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ALL_MONSTERS
    # Load monsters directly from XML via RAG module
    ALL_MONSTERS = mhw_rag.get_all_monster_names_from_xml()
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"🔥 UNHANDLED ERROR: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    history: list = []

from dotenv import load_dotenv # type: ignore
# Localizar .env na raiz do projeto (um nível acima de /backend)
env_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(env_path)

# Use the provided API Key via .env
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "Bearer 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")
if not NVIDIA_API_KEY:
    NVIDIA_API_KEY = "Bearer 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"

# Garantir que a key esteja no formato correto para o OpenAI client
OS_NVIDIA_KEY = NVIDIA_API_KEY.replace("Bearer ", "").strip()


@app.get("/monster/{name}")
async def get_monster(name: str):
    # Tentar buscar dados diretamente do banco de dados (muito mais rápido e preciso)
    try:
        data_list = mhw_api.get_monster_data(name)
        if not data_list:
            raise HTTPException(status_code=404, detail="Monstro não encontrado no banco de dados.")
        
        # Pegar o primeiro resultado (mais relevante)
        m = data_list[0]
        
        # Buscar imagem via scraping (ou cache)
        image_url = mhw_api.get_monster_image_url(m['name'])
        
        # Formatar para o frontend
        monster_intel = {
            "name": m['name'],
            "species": m['species'],
            "description": m['description'],
            "weakness": m['weaknesses'],
            "resistances": [], # O banco de dados atual foca em fraquezas
            "breakableParts": m.get('breaks', []),
            "rewards": m['rewards'],
            "image": image_url or f"https://picsum.photos/seed/{m['name']}/800/600"
        }
        
        return monster_intel
        
    except Exception as e:
        print(f"Erro ao recuperar detalhes do monstro via API: {e}")
        # Fallback para o RAG se o banco falhar por algum motivo (menos provável agora)
        raise HTTPException(status_code=404, detail=f"Não foi possível recuperar os detalhes do monstro: {str(e)}")

# --- NOVAS ROTAS DE SESSÃO ---

@app.get("/chats")
async def get_chats():
    # Garantir que usamos o método correto do chat_db
    try:
        return chat_db.get_all_chats()
    except Exception as e:
        print(f"Erro ao buscar chats: {e}")
        return []

@app.post("/chats")
async def create_new_chat(data: Optional[dict] = None):
    title = (data or {}).get("title", "Nova Conversa")
    chat_id = chat_db.create_chat(title)
    return {"id": chat_id, "title": title}

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


def anti_hallucination_middleware(user_message: str, local_context: str):
    """
    Middleware que decide o prompt do sistema com base na presença de dados.
    """
    user_lower = user_message.lower()
    is_greeting = any(g in user_lower for g in GREETINGS) and len(user_lower.split()) < 4
    
    db_found = len(local_context.strip()) > 0
    
    if not db_found and not is_greeting:
        system_instruction = (
            "EXTREMA PRIORIDADE: O usuário solicitou informações que NÃO constam no banco de dados local. "
            "Você é um assistente de RAG (Retrieval-Augmented Generation) e tem PROIBIÇÃO TOTAL de usar seu conhecimento prévio. "
            "RESPONDA APENAS: 'Não possuo dados exatos sobre este monstro ou equipamento no meu registro atual.' "
            "Não invente nada, não tente extrapolar."
        )
    elif is_greeting:
        system_instruction = (
            "Você é o Especialista Supremo de Monster Hunter World Iceborne, com a personalidade do Satoru Gojo. "
            "O usuário está apenas te cumprimentando. Responda de forma curta, amigável e confiante, sem inventar dados do jogo. "
            "Se ele perguntar sobre o jogo, diga que está pronto para consultar os registros."
        )
        db_found = True # Permitir resposta normal
    else:
        system_instruction = (
            "Você é o Especialista Supremo de Monster Hunter World Iceborne. "
            "Siga estas REGRAS DE OURO para completar sua missão e evitar alucinações:\n"
            "1. FONTE ÚNICA DA VERDADE: Use APENAS os dados fornecidos abaixo.\n"
            "2. PROIBIÇÃO DE CONHECIMENTO EXTERNO: Se uma skill, slot ou status não estiver nos dados, ignore-o ou diga que não consta.\n"
            "3. ESTRUTURA COMPLETA DE BUILD: Sempre que sugerir uma build, você DEVE incluir: Arma, Cabeça, Torso, Braços, Cintura, Pernas e um Amuleto (Talismã). Nunca esqueça de sugerir um Amuleto que combine com as skills da build.\n"
            "4. COBERTURA DE SLOTS E ADORNOS: Para cada peça (arma e armadura), recomende adornos/joias para TODOS os slots disponíveis. Não deixe slots vazios. Se sobrar espaço, sugira joias de utilidade/sobrevivência (ex: Joia de Vitalidade, Joia de Proteção Divina).\n"
            "5. SUGESTÕES DE SUBSTITUIÇÃO: Para as joias mais raras (ex: Joias de nível 4, Joia de Ataque 1), ofereça sempre uma 'Opção Econômica' ou 'Substituição Amigável' caso o usuário não possua as joias ideais.\n"
            "6. VERACIDADE: Nunca invente valores numéricos ou skills que não existam no contexto.\n"
            "7. TRATAMENTO DE PERGUNTAS VAGAS: Se o usuário perguntar de forma genérica o que você tem (ex: 'Quais joias você tem?', 'Mostre os equipamentos'), NÃO liste tudo. "
            "Reconheça o interesse e faça 2 ou 3 perguntas de qualificação: Rank desejado (MR/HR), tipo de habilidade (Ataque, Defesa, Utilidade) ou arma/estilo de jogo.\n"
            "8. SOLICITAÇÃO DE CATÁLOGO COMPRETO: Se o usuário pedir explicitamente para 'ver tudo', 'tabela completa' ou 'catálogo completo', NÃO exiba o texto no chat. "
            "Responda apenas: 'Como solicitado, aqui está o catálogo completo para sua análise detalhada: [Catálogo Completo de Joias](/catalogo_completo.md)'.\n"
            "9. CONSULTAS ESPECÍFICAS: Se o usuário já deu detalhes, responda diretamente com as opções dos dados abaixo.\n\n"
            f"DADOS RECUPERADOS DO BANCO DE DADOS:\n{local_context}"
        )
    
    return system_instruction, db_found


@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    user_lower = user_message.lower()

    # --- IDENTIFICAR CONTEXTO DE MONSTRO (Cura para o 'Alzheimer') ---
    chat_id = request.chat_id or "default_session"
    db_history = chat_db.get_chat_messages(chat_id)
    active_monster = None
    
    # 1. Procurar monstro no histórico (do mais recente para o mais antigo)
    for msg in reversed(db_history):
        content_low = msg['content'].lower()
        matched = next((str(m) for m in ALL_MONSTERS if str(m).lower() in content_low), None)
        if matched:
            active_monster = matched
            break

    # 2. Procurar monstro na mensagem ATUAL (sobrescreve o histórico se houver um novo)
    found_now = next((str(m) for m in sorted(ALL_MONSTERS, key=len, reverse=True) if str(m).lower() in user_lower), None)
    
    monster_context = found_now or active_monster
    if monster_context:
        print(f"🔍 Monstro em foco: {monster_context}")

    # --- RECUPERAR CONTEXTO RAG ---
    is_greeting = any(g in user_lower for g in GREETINGS) and len(user_lower.split()) < 4
    
    try:
        if not is_greeting:
            # Tentar RAG com a mensagem do usuário
            local_context = await mhw_rag.get_rag_context(user_message)
            
            # Se a pergunta for vaga (ex: "o que ele dropa?") e tivermos um monstro no contexto, 
            # forçar uma busca pelo monstro para alimentar o RAG
            if len(local_context.strip()) < 100 and monster_context:
                extra_context = await mhw_rag.get_rag_context(f"Detalhes, drops e fraquezas do {monster_context}")
                local_context = (local_context + "\n" + extra_context).strip()
        else:
            local_context = ""
    except Exception as e:
        print(f"❌ Erro ao recuperar contexto RAG: {e}")
        local_context = ""

    # APLICAR MIDDLEWARE ANTI-ALUCINAÇÃO
    system_instruction, has_data = anti_hallucination_middleware(user_message, local_context)
    
    # Injetar o monstro ativo no sistema para o LLM não se perder
    if monster_context:
        system_instruction += f"\n\nFOCO DA CONVERSA: Você está falando sobre o monstro '{monster_context}'. Mantenha o contexto técnico nele, a menos que eu peça sobre outro monstro explicitamente."
        has_data = True # Se temos um monstro no contexto, podemos responder

    # Personalidade do Gojo (opcional, mantida se houver dados, senão bloqueada pelo middleware)
    if has_data:
        system_instruction += (
            "\nESTILO: Responda como Satoru Gojo (arrogante, confiante, brincalhão), "
            "mas mantenha a precisão técnica dos dados acima."
        )

    # Construir mensagens para o LLM
    llm_messages = [{"role": "system", "content": system_instruction}]
    
    # Adicionar histórico (últimas 10 mensagens para não estourar contexto)
    if db_history:
        history_slice = cast(list, db_history)[-10:]
        for msg in history_slice:
            llm_messages.append({"role": msg['role'], "content": msg['content']})
        
    # Adicionar mensagem atual
    llm_messages.append({"role": "user", "content": user_message})

    # Usar AsyncOpenAI com timeout para não bloquear o event loop
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=OS_NVIDIA_KEY,
        timeout=httpx.Timeout(60.0, connect=10.0),  # 60s total, 10s para conectar
    )

    try:
        completion = await client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=llm_messages,
            temperature=0.4, # Temperatura mais baixa para mais precisão
            max_tokens=2048,
            stream=False
        )
        
        response_text = completion.choices[0].message.content

        # SALVAR NO BANCO SE TIVER CHAT_ID
        if chat_id:
            # Salvar pergunta do usuário
            chat_db.add_message(chat_id, "user", user_message)
            # Salvar resposta da IA
            chat_db.add_message(chat_id, "assistant", response_text)
            
            # Se for a primeira mensagem, atualizar título baseado na pergunta
            if not db_history:
                msg_str = str(user_message)
                new_title = msg_str[:30] + ("..." if len(msg_str) > 30 else "")
                chat_db.update_chat_title(chat_id, new_title)

        return {
            "response": response_text, 
            "sources": ["MHW RAG"] if has_data else [],
            "detected_monster": monster_context,
            "chat_id": chat_id
        }
    except httpx.TimeoutException:
        error_detail = "A API demorou demais para responder. Tente novamente."
        print(f"⏰ Timeout: {error_detail}")
        raise HTTPException(status_code=504, detail=error_detail)
    except Exception as e:
        error_detail = f"API Error: {str(e)}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)

# --- CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS ---
# Definir caminhos fora de condicionais para evitar erros de escopo
backend_dir_abs = os.path.dirname(os.path.abspath(__file__))
root_dir_abs = os.path.dirname(backend_dir_abs)
dist_dir_abs = os.path.join(root_dir_abs, "frontend", "dist")

if os.path.exists(dist_dir_abs):
    frontend_dir_final = dist_dir_abs
    print(f"🚀 Servindo frontend a partir de: {frontend_dir_final}")
else:
    frontend_dir_final = os.path.join(root_dir_abs, "frontend")
    print(f"⚠️ Atenção: 'dist' não encontrado. Servindo de: {frontend_dir_final}")

app.mount("/", StaticFiles(directory=frontend_dir_final, html=True), name="frontend")

if __name__ == "__main__":

    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

    def run_app():

        # Iniciar servidor FastAPI em background
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Caminho da Splash Screen
        # No executável, BASE_DIR aponta para a raiz temporária onde os arquivos estão
        splash_path = os.path.join(BASE_DIR, "backend", "splash.html")
        
        # Se não encontrar (fallback para dev em outras estruturas)
        if not os.path.exists(splash_path):
            splash_path = os.path.join(os.path.dirname(__file__), "splash.html")

        # Pegar as dimensões da tela (monitor principal)
        screens = webview.active_window().screens if webview.active_window() else webview.screens
        screen = screens[0]
        sw, sh = screen.width, screen.height
        
        # Dimensões da Splash
        sp_w, sp_h = 500, 350
        sp_x = (sw - sp_w) // 2
        sp_y = (sh - sp_h) // 2

        # Criar a janela da Splash centralizada
        splash = webview.create_window(
            "MHW:I Assistant - Loading", 
            splash_path, 
            width=sp_w, height=sp_h, 
            x=sp_x, y=sp_y,
            frameless=True, on_top=True, resizable=False
        )

        def perform_update():
            time.sleep(1) # Pequena pausa para a splash carregar
            
            def on_progress(text, progress):
                # Envia o status para o JS da Splash de forma segura
                # Se progress for None, mantém a porcentagem atual na barra
                prog_js = progress if progress is not None else "undefined"
                safe_text = json.dumps(text)
                splash.evaluate_js(f"updateStatus({safe_text}, {prog_js})")
            
            # Capturar logs do sistema e enviar para a Splash
            handler = SplashLogHandler(on_progress)
            logging.getLogger().addHandler(handler)
            logging.getLogger().setLevel(logging.INFO)
            
            # Redirecionar stdout para capturar prints de bibliotecas (como gdown)
            original_stdout = sys.stdout
            sys.stdout = SplashStdout(on_progress, original_stdout)
            
            # Rodar o updater
            try:
                updater.update_app(progress_callback=on_progress)
            except Exception as e:
                on_progress(f"Erro no update: {str(e)}", 100)
                time.sleep(2)

            # Inicializar motor RAG
            
            try:
                # Inicializa o motor RAG enviando o callback para feedback na Splash
                mhw_rag.setup_rag_engine(progress_callback=on_progress)
            except Exception as e:
                print(f"Erro ao inicializar RAG: {e}")
            
            on_progress("Iniciando assistente...", 100)
            time.sleep(1)

            # Iniciar watcher de XMLs após RAG estar pronto
            rag_pipeline.start_watcher()
            
            # Restaurar stdout original
            sys.stdout = original_stdout
            logging.getLogger().removeHandler(handler)
            
            # Dimensões da Principal
            mw, mh = 1200, 800
            mx = (sw - mw) // 2
            my = (sh - mh) // 2

            # Criar janela principal centralizada
            main_win = webview.create_window(
                "MHW:I AI Assistant", 
                "http://127.0.0.1:8000", 
                width=mw, height=mh,
                x=mx, y=my,
                min_size=(800, 600)
            )
            # Fechar splash e mostrar principal
            splash.destroy()

        # Iniciar o loop do webview
        webview.start(perform_update)

    run_app()
