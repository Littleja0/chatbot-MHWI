import asyncio
import os
import json
import sys
from pathlib import Path

# Adicionar caminhos para importação
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "backend" / "src"))

from core.mhw.mhw_tools import search_armor, MHW_TOOLS

async def test_tool_calling():
    print("🧪 Testando lógica de Tool Calling (Simulada)...")
    
    # Simular uma pergunta de build
    user_message = "Me recomende um elmo de Master Rank que tenha a skill Health Boost."
    
    # Na vida real, a LLM veria a ferramenta e decidiria chamar.
    # Aqui vamos chamar a função diretamente para ver se o SQL funciona.
    print(f"User: {user_message}")
    
    # Simulando o que a LLM passaria como argumentos
    args = {
        "skills": ["Health Boost"],
        "rank": "MR",
        "piece_type": "Head"
    }
    
    print(f"🛠️ Chamando search_equipment com {args}...")
    result = search_armor(**args)
    
    data = json.loads(result)
    print(f"✅ Encontradas {len(data)} peças.")
    if data:
        print(f"📝 Primeira peça: {data[0]['name']} - Skills: {data[0]['skills']}")

if __name__ == "__main__":
    asyncio.run(test_tool_calling())
