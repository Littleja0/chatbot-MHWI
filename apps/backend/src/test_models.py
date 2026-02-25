import asyncio
import json
import os
from openai import AsyncOpenAI
import httpx

async def debug():
    print("Testing with different models...")
    # Get original config
    from core.config import NVIDIA_API_KEY, LLM_BASE_URL
    from core.mhw.mhw_tools import MHW_TOOLS
    
    client = AsyncOpenAI(
        base_url=LLM_BASE_URL,
        api_key=NVIDIA_API_KEY,
        timeout=httpx.Timeout(20.0)
    )
    
    models_to_test = [
        "moonshotai/kimi-k2-instruct-0905",
        "meta/llama-3.1-8b-instruct"
    ]
    
    for model in models_to_test:
        print(f"\n--- Testing Model: {model} ---")
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Diga oi"}],
                tools=MHW_TOOLS,
                max_tokens=50
            )
            print(f"SUCCESS with {model}")
            print("Tool calls:", response.choices[0].message.tool_calls)
        except Exception as e:
            print(f"FAILED with {model}: {e}")

if __name__ == "__main__":
    asyncio.run(debug())
