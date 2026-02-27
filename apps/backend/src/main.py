"""
main.py — Entry point limpo do backend MHW Chatbot.

Responsabilidades:
- Inicializar a aplicação FastAPI
- Montar routers
- Servir arquivos estáticos do frontend
- Iniciar servidor + webview
"""

import sys
import os
import threading
import time
import traceback
from pathlib import Path

# Garantir que o diretório 'src' esteja no path para imports relativos funcionarem
_src_dir = str(Path(__file__).resolve().parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from contextlib import asynccontextmanager

import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore

from core.config import HOST, PORT, ROOT_DIR
from core.logging import log

# Log do ambiente de inicialização
log.info(f"=== MHW Chatbot Startup ===")
log.info(f"Python: {sys.version}")
log.info(f"Frozen: {getattr(sys, 'frozen', False)}")
log.info(f"ROOT_DIR: {ROOT_DIR}")
log.info(f"CWD: {os.getcwd()}")
if getattr(sys, 'frozen', False):
    log.info(f"_MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
    log.info(f"Executable: {sys.executable}")

# Imports com tratamento de erro
try:
    from api.routers.chat import router as chat_router, init_skill_caps
    from api.routers.monsters import router as monsters_router
    from api.routers.equipment import router as equipment_router
    from services.monster_service import get_all_monster_names, get_all_skill_caps
    log.info("All modules imported successfully.")
except Exception as e:
    log.error(f"Failed to import modules: {e}")
    log.error(traceback.format_exc())


# --- App Lifecycle ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        log.info("Lifespan: Loading monster data...")
        all_monsters = get_all_monster_names()
        log.info(f"Lifespan: Loaded {len(all_monsters)} monsters.")
        
        skill_caps = get_all_skill_caps()
        init_skill_caps(skill_caps)
        log.info(f"Lifespan: Loaded {len(skill_caps)} skill caps.")
    except Exception as e:
        log.error(f"Lifespan: Failed to load data: {e}")
        log.error(traceback.format_exc())
    yield


# --- App Setup ---

app = FastAPI(lifespan=lifespan, title="MHW:I Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Error Handling ---

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    log.error(f"UNHANDLED ERROR: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )


# --- Mount Routers ---


app.include_router(chat_router)
app.include_router(monsters_router)
app.include_router(equipment_router)


# --- Static Files (Frontend) ---
frontend_dist = ROOT_DIR / "apps" / "frontend" / "dist"

if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
    log.info(f"Serving frontend from: {frontend_dist}")
else:
    log.warning(f"Frontend not found at {frontend_dist}")


# --- Server Startup ---

def run_server():
    try:
        log.info(f"Starting uvicorn on {HOST}:{PORT}...")
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
    except Exception as e:
        log.error(f"Uvicorn failed: {e}")
        log.error(traceback.format_exc())


if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    import socket
    log.info("Waiting for server to start...")
    server_ready = False
    for i in range(60):  # Aguarda até 30 segundos
        try:
            with socket.create_connection((HOST, PORT), timeout=1):
                server_ready = True
                log.info(f"Server is ready! (took {i * 0.5:.1f}s)")
                break
        except OSError:
            time.sleep(0.5)

    if not server_ready:
        log.error("Server did NOT start within 30 seconds!")

    try:
        import webview  # type: ignore
        url = f"http://localhost:{PORT}"
        log.info(f"Opening webview window at {url}...")
        webview.create_window("Monster Hunter World Chatbot", url, width=1200, height=800)
        webview.start()
    except Exception as e:
        log.error(f"Failed to start webview: {e}")
        log.error(traceback.format_exc())
        while True:
            time.sleep(1)
