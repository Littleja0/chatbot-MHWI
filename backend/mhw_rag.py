import os
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.llms.nvidia import NVIDIA
from llama_index.embeddings.nvidia import NVIDIAEmbedding

# Configurações do NVIDIA AI Foundation
NVIDIA_API_KEY = "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"
os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY

# Configurar o LlamaIndex para usar NVIDIA
Settings.llm = NVIDIA(model="moonshotai/kimi-k2-instruct-0905")
Settings.embed_model = NVIDIAEmbedding(model="nvidia/nv-embedqa-e5-v5", truncate="END")

# Caminhos
RAG_PATH = Path("rag")
STORAGE_PATH = Path("storage")

# Instância global do motor
_query_engine = None

def setup_rag_engine():
    """
    Inicializa o motor de RAG e configura a instância global.
    """
    global _query_engine
    if _query_engine is not None:
        return _query_engine

    if not RAG_PATH.exists():
        print(f"Erro: Pasta {RAG_PATH} não encontrada!")
        return None

    if STORAGE_PATH.exists() and any(STORAGE_PATH.iterdir()):
        print("Carregando índice RAG existente da pasta storage...")
        storage_context = StorageContext.from_defaults(persist_dir=str(STORAGE_PATH))
        index = load_index_from_storage(storage_context)
    else:
        print("Criando novo índice RAG a partir dos arquivos XML (isso pode demorar uma vez)...")
        reader = SimpleDirectoryReader(input_dir=str(RAG_PATH), required_exts=[".xml"])
        documents = reader.load_data()
        
        index = VectorStoreIndex.from_documents(documents)
        
        STORAGE_PATH.mkdir(exist_ok=True)
        index.storage_context.persist(persist_dir=str(STORAGE_PATH))
        print("Índice RAG persistido e pronto.")

    _query_engine = index.as_query_engine(similarity_top_k=5)
    return _query_engine

def get_rag_context(prompt: str):
    """
    Recupera apenas os trechos de contexto (XML) relevantes para a pergunta,
    sem chamar o LLM no final. Útil para integrar com o prompt já existente.
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = setup_rag_engine()
        
    if _query_engine:
        # Usamos o retriever interno do query engine
        retriever = _query_engine._retriever
        nodes = retriever.retrieve(prompt)
        # Junta os textos dos nodes encontrados
        context = "\n".join([node.get_content() for node in nodes])
        return context
    return ""

def get_all_monster_names_from_xml():
    """
    Extrai todos os nomes de monstros do arquivo monster_text.xml (PT e EN).
    Isso substitui a necessidade do mhw.db para essa função.
    """
    import xml.etree.ElementTree as ET
    monster_text_path = RAG_PATH / "monster_text.xml"
    if not monster_text_path.exists():
        return []

    names = set()
    try:
        tree = ET.parse(monster_text_path)
        root = tree.getroot()
        for record in root.findall("DATA_RECORD"):
            lang = record.find("lang_id")
            name = record.find("name")
            if lang is not None and lang.text in ["pt", "en"] and name is not None and name.text:
                names.add(name.text)
    except Exception as e:
        print(f"Erro ao extrair nomes do XML: {e}")
    
    return list(names)

def get_rag_response(prompt: str):
    """
    Busca a resposta utilizando o motor de RAG.
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = setup_rag_engine()
        
    if _query_engine:
        response = _query_engine.query(prompt)
        return str(response)
    return "Erro ao inicializar o motor de RAG."

if __name__ == "__main__":
    # Teste rápido
    print("Iniciando teste do RAG...")
    query = "Quais são as fraquezas do Rathalos e seus drops principais?"
    print(f"Pergunta: {query}")
    print(f"Resposta: {get_rag_response(query)}")
