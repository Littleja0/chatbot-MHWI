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
import mhw_rag # type: ignore
import rag_pipeline # type: ignore
import updater # type: ignore
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
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import BaseModel  # type: ignore
from openai import AsyncOpenAI  # type: ignore
from contextlib import asynccontextmanager

# Cache monster names for entity extraction
ALL_MONSTERS = []

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

class ChatRequest(BaseModel):
    message: str

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
    # Usamos o RAG para extrair os detalhes específicos em formato JSON
    # Isso elimina a necessidade de queries SQL complexas
    prompt = (
        f"Extraia os detalhes do monstro '{name}' no seguinte formato JSON estrito: "
        '{"name": "nome", "species": "espécie", "description": "descrição", '
        '"weakness": ["lista"], "resistances": ["lista"], "breakableParts": ["lista"], '
        '"rewards": {"Rank": [{"item": "nome", "condition": "condição", "chance": "20%", "stack": 1}]}}'
        "Responda APENAS o JSON."
    )
    
    import json
    try:
        raw_response = mhw_rag.get_rag_response(prompt)
        # Limpa possíveis formatações de markdown do LLM
        json_str = raw_response.strip().replace("```json", "").replace("```", "")
        monster_data = json.loads(json_str)
        
        # Adiciona a imagem (fallback para imagem aleatória se não tiver scraper)
        monster_data["image"] = f"https://picsum.photos/seed/{name}/800/600"
        return monster_data
    except Exception as e:
        print(f"Erro ao parsear detalhes do monstro via RAG: {e}")
        raise HTTPException(status_code=404, detail="Não foi possível recuperar os detalhes do monstro.")

def anti_hallucination_middleware(user_message: str, local_context: str):
    """
    Middleware que decide o prompt do sistema com base na presença de dados.
    """
    user_lower = user_message.lower()
    greetings = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "opa", "hello", "hi"]
    is_greeting = any(g in user_lower for g in greetings) and len(user_lower.split()) < 4
    
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
            "Siga estas REGRAS DE OURO para evitar alucinações:\n"
            "1. FONTE ÚNICA DA VERDADE: Use APENAS os dados fornecidos abaixo.\n"
            "2. PROIBIÇÃO DE CONHECIMENTO EXTERNO: Se uma skill, slot ou status não estiver nos dados, ignore-o ou diga que não consta.\n"
            "3. LISTA ESTRUTURADA: Para builds, use o formato sugerido (Cabeça, Torso, Braços, Cintura, Pernas, Talismã).\n"
            "4. VERACIDADE: Nunca invente valores numéricos.\n\n"
            f"DADOS RECUPERADOS DO BANCO DE DADOS:\n{local_context}"
        )
    
    return system_instruction, db_found


@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message
    user_lower = user_message.lower()

    # Detectar monstro mencionado (para metadata da resposta)
    sorted_monsters = sorted(ALL_MONSTERS, key=len, reverse=True)
    found_monster = next((str(m) for m in sorted_monsters if str(m).lower() in user_lower), None)

    # Verificar se é cumprimento simples
    greetings = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "opa", "hello", "hi"]
    is_greeting = any(g in user_lower for g in greetings) and len(user_lower.split()) < 4

    if not is_greeting:
        local_context = await asyncio.to_thread(mhw_rag.get_rag_context, user_message)
    else:
        local_context = ""

    # APLICAR MIDDLEWARE ANTI-ALUCINAÇÃO
    system_instruction, has_data = anti_hallucination_middleware(user_message, local_context)
    
    # Personalidade do Gojo (opcional, mantida se houver dados, senão bloqueada pelo middleware)
    if has_data:
        system_instruction += (
            "\nESTILO: Responda como Satoru Gojo (arrogante, confiante, brincalhão), "
            "mas mantenha a precisão técnica dos dados acima."
        )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_message}
    ]

    # Usar AsyncOpenAI com timeout para não bloquear o event loop
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=OS_NVIDIA_KEY,
        timeout=httpx.Timeout(60.0, connect=10.0),  # 60s total, 10s para conectar
    )

    try:
        completion = await client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=messages,
            temperature=0.4, # Temperatura mais baixa para mais precisão
            max_tokens=2048,
            stream=False
        )
        return {
            "response": completion.choices[0].message.content, 
            "sources": ["MHW RAG (XMLs estruturados)"] if has_data else [],
            "detected_monster": found_monster
        }
    except httpx.TimeoutException:
        error_detail = "A API demorou demais para responder. Tente novamente."
        print(f"⏰ Timeout: {error_detail}")
        raise HTTPException(status_code=504, detail=error_detail)
    except Exception as e:
        error_detail = f"API Error: {str(e)}"
        print(f"❌ {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)

# Mount the frontend directory to serve static files
if getattr(sys, 'frozen', False):
    frontend_dir = os.path.join(os.path.dirname(sys.executable), "frontend")
else:
    # Use absolute paths based on this file's location
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(backend_dir)
    dist_dir = os.path.join(root_dir, "frontend", "dist")
    
    if os.path.isdir(dist_dir):
        frontend_dir = dist_dir
    else:
        frontend_dir = os.path.join(root_dir, "frontend")

app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

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
