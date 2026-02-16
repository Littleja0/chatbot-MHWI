"""
chat.py — Router de chat (rotas /chat, /chats).
"""

from typing import Optional
from fastapi import APIRouter, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore

from data.db import (
    get_all_chats, create_chat, get_chat_messages,
    delete_chat, toggle_pin, update_chat_title,
    get_user_config, set_user_config
)
from services.chat_service import process_chat
from services.monster_service import get_rag_context, get_all_skill_caps

router = APIRouter()

# --- State (populated at startup) ---
_skill_caps: dict = {}


def init_skill_caps(caps: dict):
    """Chamado no startup para popular os caps."""
    global _skill_caps
    _skill_caps = caps


# --- Models ---

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    history: list = []


# --- Chat Management ---

@router.get("/chats")
async def list_chats():
    return get_all_chats()


@router.post("/chats")
async def new_chat(data: Optional[dict] = None):
    title = (data or {}).get("title", "Nova Conversa")
    return {"id": create_chat(title), "title": title}


@router.get("/chats/{chat_id}/history")
async def get_history(chat_id: str):
    return get_chat_messages(chat_id)


@router.delete("/chats/{chat_id}")
async def remove_chat(chat_id: str):
    delete_chat(chat_id)
    return {"status": "deleted"}


@router.patch("/chats/{chat_id}/pin")
async def pin_chat(chat_id: str):
    toggle_pin(chat_id)
    return {"status": "toggled"}


@router.patch("/chats/{chat_id}/title")
async def rename_chat(chat_id: str, data: dict):
    title = data.get("title")
    update_chat_title(chat_id, title)
    return {"status": "renamed"}


# --- Chat Endpoint ---

@router.post("/chat")
async def chat(request: ChatRequest):
    chat_id = request.chat_id or "default_session"

    try:
        result = await process_chat(
            user_message=request.message,
            chat_id=chat_id,
            skill_caps=_skill_caps,
            get_rag_context_fn=get_rag_context,
        )
        return result
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout da API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- User Profile ---

@router.get("/user/profile")
async def get_profile():
    return {
        "mr": get_user_config("mr", 1),
        "hr": get_user_config("hr", 0),
        "jewels": get_user_config("jewels", {}),
        "save_path": get_user_config("save_path", None)
    }


@router.post("/user/profile")
async def update_profile(data: dict):
    if "mr" in data:
        set_user_config("mr", data["mr"])
    if "hr" in data:
        set_user_config("hr", data["hr"])
    if "jewels" in data:
        set_user_config("jewels", data["jewels"])
    return {"status": "updated"}


@router.post("/user/sync-save")
async def sync_save():
    return {
        "status": "manual_only",
        "message": "Sincronização automática desativada temporariamente."
    }
