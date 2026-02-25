# Proposal: Fix RAG Hallucination and Cleanup Jewels

## Why
O chatbot está "alucinando" detalhes técnicos de equipamentos (níveis de skills e slots) pois o RAG recupera nomes de peças, mas nem sempre o contexto completo das mesmas. A personalidade criativa (Satoru Gojo) acaba preenchendo as lacunas com informações incorretas. Além disso, existe uma funcionalidade legada de "inventário de joias" que não funciona mais como pretendido e polui o contexto.

## What Changes
1. **Remoção das Joias**: Eliminar a referência ao inventário de joias no prompt do sistema e remover os dados obsoletos do `sessions.db`.
2. **Camada de Enriquecimento (SQL-Backed RAG)**: Implementar uma lógica que identifica nomes de equipamentos (armaduras/armas) no contexto retornado pelo RAG e busca os stats exatos no SQLite (`mhw.db`) antes de enviar o prompt final à LLM.
3. **Blindagem de Prompt**: Atualizar as instruções do sistema para proibir explicitamente a invenção de stats numéricos.

## Impacted Capabilities
- `chat-service`: Modificação da construção do prompt e limpeza de joias.
- `rag-verification`: Nova funcionalidade de validação cruzada entre RAG e SQL.

## Impact
- **Backend API**: Adição de uma etapa de processamento pós-RAG no `chat_service.py`.
- **Database**: Limpeza de entradas na tabela `user_config` do `sessions.db`.
- **Qualidade da Resposta**: Respostas técnicas 100% precisas em relação a slots e skills base.
