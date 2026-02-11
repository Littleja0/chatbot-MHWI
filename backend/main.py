import sys
import os

# Ajustar sys.path IMEDIATAMENTE para encontrar módulos na raiz
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import mhw_rag  # type: ignore
import updater  # type: ignore
import json
import uvicorn  # type: ignore
import webview  # type: ignore
import threading
import time
import requests # type: ignore

from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from pydantic import BaseModel  # type: ignore
from openai import OpenAI  # type: ignore
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

# Use the provided API Key
NVIDIA_API_KEY = "Bearer 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"
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


def format_skill_list(skills):
    """Format a list of skills as a string."""
    if not skills:
        return ""
    return ", ".join([f"{s['name']} Lv{s['level']}" for s in skills])


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
    
    local_context_parts: list[str] = []
    
    # === KEYWORDS PARA DETECÇÃO DE CONTEXTO ===
    keywords = {
        "armor": ["armadura", "armor", "capacete", "elmo", "helm", "head", "peitoral", 
                  "chest", "mail", "braços", "arms", "vambraces", "cintura", 
                  "waist", "coil", "pernas", "legs", "greaves", "set", "slots", "habilidade", "skill", "status"],
        "weapon": ["arma", "weapon", "espada", "sword", "martelo", "hammer", "lança", 
                   "lance", "machado", "axe", "arco", "bow", "gunlance", "glaive", 
                   "dual blades", "espadas duplas", "great sword", "long sword",
                   "heavy bowgun", "light bowgun", "hunting horn", "switch axe",
                   "charge blade", "insect glaive", "atk", "ataque", "sharpness", "afiação"],
        "decoration": ["adorno", "decoration", "jewel", "joia", "gema", "slot"],
        "charm": ["amuleto", "charm", "talismã", "talisman"],
        "quest": ["missão", "quest", "caçada", "hunt", "expedição", "guiding lands"],
        "tool": ["manto", "mantle", "ferramenta", "tool", "booster"],
        "skill": ["skill", "habilidade", "talent", "talento"],
        "kinsect": ["kinsect", "inseto", "glaive inseto"]
    }
    
    detected_types = [t for t, kws in keywords.items() if any(kw in user_lower for kw in kws)]
    
    # === BUSCAR MONSTRO ===
    sorted_monsters = sorted(ALL_MONSTERS, key=len, reverse=True)
    found_monster = next((str(m) for m in sorted_monsters if str(m).lower() in user_lower), None)
    
    # === PROCESSAMENTO DE DADOS (RAG) ===
    
    # === PROCESSAMENTO DE DADOS (RAG via LlamaIndex) ===
    # Agora em vez de queries manuais no SQL, o LlamaIndex busca nos XMLs da pasta /rag
    
    greetings = ["olá", "oi", "bom dia", "boa tarde", "boa noite", "e aí", "opa", "hello", "hi"]
    is_greeting = any(g in user_lower for g in greetings) and len(user_lower.split()) < 4

    if not is_greeting:
        local_context = mhw_rag.get_rag_context(user_message)
    else:
        local_context = "" # Ignora busca pesada para cumprimentos
    
    has_data = len(local_context.strip()) > 0
    
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

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

    try:
        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct-0905",
            messages=messages,
            temperature=0.4, # Temperatura mais baixa para mais precisão
            max_tokens=2048,
            stream=False
        )
        return {
            "response": completion.choices[0].message.content, 
            "sources": ["Local DB (mhw.db)"] if has_data else [],
            "detected_monster": found_monster
        }
    except Exception as e:
        print(f"Error calling NVIDIA API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    import uvicorn  # type: ignore
    import threading
    import webview  # type: ignore

    
    # SQLite update is disabled as we are now source-of-truth XML
    # try:
    #     auto_update_db.quick_update()
    # except Exception as e:
    #     print(f"Update check failed: {e}")

    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

    def run_app():

        # Iniciar servidor FastAPI em background
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Caminho da Splash Screen
        if getattr(sys, 'frozen', False):
            splash_path = os.path.join(os.path.dirname(sys.executable), "backend", "splash.html")
        else:
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
                safe_text = json.dumps(text)
                splash.evaluate_js(f"updateStatus({safe_text}, {progress})")
            
            # Rodar o updater
            try:
                updater.update_app(progress_callback=on_progress)
            except Exception as e:
                on_progress(f"Erro no update: {str(e)}", 100)
                time.sleep(2)

            # Transição para o App principal
            on_progress("Carregando base de dados RAG...", 90)
            try:
                # Inicializa o motor RAG (cria índice se não existir)
                mhw_rag.setup_rag_engine()
            except Exception as e:
                print(f"Erro ao inicializar RAG: {e}")
            
            on_progress("Iniciando assistente...", 100)
            time.sleep(1)
            
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
