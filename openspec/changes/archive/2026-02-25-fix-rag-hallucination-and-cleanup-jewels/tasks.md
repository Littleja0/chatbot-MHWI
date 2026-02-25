# Tasks

## 1. Limpeza de Dados Legados (Joias)

- [x] 1.1 Remover a lógica de busca de `user_jewels` no `chat_service.py:anti_hallucination_middleware`.
- [x] 1.2 Criar um script temporário ou adicionar lógica de inicialização para remover a chave `jewels` da tabela `user_config` no `sessions.db`.
- [x] 1.3 Remover a exibição do inventário de joias no prompt do sistema.

## 2. Implementação da Camada de Verificação SQL

- [x] 2.1 Implementar função de extração de peças/armas do `local_context` usando Regex no `chat_service.py`.
- [x] 2.2 Implementar loop no `process_chat` para consultar `get_armor_details` e `get_weapon_details` (de `mhw_tools.py`) para cada item identificado.
- [x] 2.3 Formatar os dados técnicos retornados em uma string estruturada para o prompt.

## 3. Blindagem de Prompt e Integração Final

- [x] 3.1 Unificar o contexto do RAG com a nova seção `DADOS TÉCNICOS VERIFICADOS (SQL)`.
- [x] 3.2 Atualizar o `system_instruction` com as "Regras de Ouro" de proibição de invenção de slots/skills.
- [x] 3.3 Validar a resposta do LLM com uma pergunta de teste (ex: "Build de gelo atualizada").
