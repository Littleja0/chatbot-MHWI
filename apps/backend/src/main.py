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

# Garantir imports funcionem a partir desta localização
_this_dir = os.path.dirname(os.path.abspath(__file__))
_apps_dir = os.path.dirname(os.path.dirname(_this_dir))
_root_dir = os.path.dirname(_apps_dir)

for p in [_this_dir, _apps_dir, _root_dir, os.path.join(_root_dir, "backend")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager

import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore

from core.config import HOST, PORT, ROOT_DIR
from core.logging import log
from api.routers.chat import router as chat_router, init_skill_caps
from api.routers.memory import router as memory_router
from api.routers.monsters import router as monsters_router
from services.monster_service import get_all_monster_names, get_all_skill_caps


# --- App Lifecycle ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        all_monsters = get_all_monster_names()
        skill_caps = get_all_skill_caps()
        init_skill_caps(skill_caps)
        log.info(f"Loaded {len(all_monsters)} monsters and {len(skill_caps)} skill caps.")
    except Exception as e:
        log.error(f"Failed to load data: {e}")
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
app.include_router(memory_router)
app.include_router(monsters_router)


# --- Static Files (Frontend) ---

# Tentar novo caminho primeiro, fallback para antigo
frontend_dist = os.path.join(_apps_dir, "frontend", "dist")
if not os.path.exists(frontend_dist):
    frontend_dist = os.path.join(_root_dir, "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    log.warning(f"Frontend not found at {frontend_dist}")


# --- Server Startup ---

def run_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    time.sleep(1.5)

    try:
        import webview  # type: ignore
        log.info("Opening window...")
        webview.create_window("Monster Hunter World Chatbot", f"http://localhost:{PORT}", width=1200, height=800)
        webview.start()
    except Exception as e:
        log.error(f"Failed to start webview: {e}")
        while True:
            time.sleep(1)
