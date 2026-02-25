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
from api.routers.chat import router as chat_router, init_skill_caps
from api.routers.monsters import router as monsters_router
from api.routers.equipment import router as equipment_router
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
app.include_router(monsters_router)
app.include_router(equipment_router)


# --- Static Files (Frontend) ---
frontend_dist = ROOT_DIR / "apps" / "frontend" / "dist"

if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
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
