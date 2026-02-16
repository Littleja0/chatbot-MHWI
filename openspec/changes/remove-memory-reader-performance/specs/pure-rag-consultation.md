# Spec: pure-rag-consultation

## ADDED Requirements

### Requirement: Desativação do Leitor de Memória
O sistema não deve importar ou inicializar o `memory_reader.py`. Nenhuma tentativa de Scan de Memória deve ocorrer.

#### Scenario: Inicialização do Servidor
- **WHEN** O servidor `main.py` é iniciado.
- **THEN** O log deve mostrar apenas a inicialização do FastAPI e do motor de RAG, sem erros de Pymem ou Admin.

### Requirement: Chat Puramente Baseado em RAG
O contexto enviado para a LLM deve conter apenas dados recuperados dos XMLs via RAG e dados do perfil persistido.

#### Scenario: Pergunta sobre Monstro
- **WHEN** O usuário pergunta sobre um monstro.
- **THEN** A IA deve responder usando os dados do XML, sem referenciar HP ou status em tempo real do jogo.
