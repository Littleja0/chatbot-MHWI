import asyncio
import sys
import os
from pathlib import Path

# Adicionar caminhos
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "apps" / "backend" / "src"))

from services.chat_service import process_chat

async def mock_get_rag(query, history=None):
    return "Dados de exemplo para o RAG. (Vazio para forçar Tool Calling)"

async def test_chat_with_tools():
    print("🤖 Testando Process Chat com Tool Calling...")
    
    # Pergunta técnica
    msg = "Gojo, me mostre as peças de cabeça do Master Rank que dão Olho Crítico (Critical Eye)."
    
    try:
        result = await process_chat(
            user_message=msg,
            chat_id="test_id",
            skill_caps={},
            get_rag_context_fn=mock_get_rag
        )
        print("\n--- Resposta do Gojo ---")
        print(result["response"])
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    # Simular NVIDIA_API_KEY se não estiver no ambiente
    if not os.getenv("NVIDIA_API_KEY"):
        print("⚠️ NVIDIA_API_KEY não encontrada. O teste de LLM real vai falhar.")
    
    import os
    asyncio.run(test_chat_with_tools())
