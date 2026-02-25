# Design: Fix RAG Hallucination and Cleanup Jewels

## Goal
Implementar uma camada de verificação técnica que elimine alucinações de stats de equipamentos no chatbot e remover dados legados de joias para limpar o contexto da LLM.

## Architecture
A solução baseia-se em interceptar o fluxo entre a recuperação do RAG e a chamada à LLM para injetar dados estruturados de alta fidelidade.

### 1. Limpeza de Dados (Cleanup)
- **Database**: Remover a chave `jewels` da tabela `user_config` no `sessions.db`.
- **Logic**: Alterar `anti_hallucination_middleware` para não buscar mais `user_jewels`.

### 2. Camada de Enriquecimento (Verification Layer)
- **Extração de Entidades**: No `chat_service.py`, após receber o `local_context` do RAG, utilizaremos expressões regulares para identificar nomes de peças e armas conhecidas (ex: "Legiana Helm", "Kjárr Sword").
- **Lookup SQL**: Para cada entidade identificada, chamaremos `get_armor_details` ou `get_weapon_details` de `mhw_tools.py`.
- **Injeção de Contexto Hard-Verify**: Os dados retornados serão formatados em uma nova seção do prompt do sistema chamada `DADOS TÉCNICOS VERIFICADOS (SQL)`.

### 3. Blindagem de Prompt
- O prompt do sistema será modificado para instruir a LLM a priorizar os dados da seção `SQL` sobre o `RAG`.
- Inclusão de uma diretiva de "Zero-Tolerance" para invenção de slots (ex: se o SQL disser que a peça tem slots [4, 1], a IA não pode sugerir que ela tem slot [2]).

## Risks / Trade-offs
- **Performance**: O lookup SQL adicional para até 15 peças (limite do RAG) pode adicionar alguns milissegundos à latência da resposta, mas o SQLite é rápido o suficiente para que o impacto seja imperceptível.
- **Divergência RAG vs SQL**: Embora raro, se o RAG achar um item que não existe no SQL, o sistema deve tratar o erro e informar que não possui os dados técnicos verificados para aquela peça específica.
