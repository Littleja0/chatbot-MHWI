import asyncio
import json
import os
import sys
from openai import AsyncOpenAI
import httpx

# Add apps/backend/src to sys.path
sys.path.append(os.path.join(os.getcwd(), "apps", "backend", "src"))

from core.config import NVIDIA_API_KEY, LLM_BASE_URL, LLM_MODEL
from core.mhw.mhw_tools import MHW_TOOLS

async def test_kimi_grammar():
    client = AsyncOpenAI(
        base_url=LLM_BASE_URL,
        api_key=NVIDIA_API_KEY,
        timeout=httpx.Timeout(20.0)
    )
    
    print(f"Testing grammar for model: {LLM_MODEL}")
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "Monte uma build"}],
            tools=MHW_TOOLS,
            max_tokens=50
        )
        print("SUCCESS! No grammar error.")
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_kimi_grammar())
