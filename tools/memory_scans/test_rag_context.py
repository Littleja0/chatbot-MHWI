
import sys
import os
import io
import asyncio
from pathlib import Path

sys.path.append(os.path.join(os.getcwd(), "backend"))
import mhw_rag # type: ignore

async def test_context():
    prompt = "me de informações do set da armadura óssea do RM, com skills, slots e armaduras"
    context = await mhw_rag.get_rag_context(prompt)
    with open("retrieved_context.txt", "w", encoding="utf-8") as f:
        f.write(context)
    print("Context saved to retrieved_context.txt")

if __name__ == "__main__":
    asyncio.run(test_context())
