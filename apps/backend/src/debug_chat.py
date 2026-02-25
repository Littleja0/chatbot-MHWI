import asyncio
import json
from services.chat_service import process_chat
from services.monster_service import get_rag_context

async def debug():
    print("Testing process_chat with current tools...")
    skill_caps = {"Ataque": 7, "Olho Crítico": 7}
    try:
        result = await process_chat(
            user_message="Monte uma build de Longsword para o Fatalis",
            chat_id="debug_test",
            skill_caps=skill_caps,
            get_rag_context_fn=get_rag_context
        )
        print("Result:", result)
    except Exception as e:
        print("Caught Exception in debug script:", e)

if __name__ == "__main__":
    asyncio.run(debug())
