# Spec: Single Source of Truth (SSoT)

## Requirements

### Requirement: Centralização de Dados
- **GIVEN** que existem pastas de dados duplicadas em `apps/backend/src/data` e `data/` (root).
- **WHEN** o sistema for inicializado.
- **THEN** ele deve carregar exclusivamente os bancos de dados (`mhw.db`, `sessions.db`) e arquivos RAG (XML) localizados na pasta `data/` da raiz do projeto.

### Requirement: Remoção de Redundância
- **GIVEN** a existência da pasta `apps/backend/src/data`.
- **WHEN** a refatoração for aplicada.
- **THEN** a pasta `apps/backend/src/data` deve ser removida permanentemente para evitar confusão de desenvolvimento.

### Requirement: Consistência de Configuração
- **GIVEN** as variáveis `MHW_DB_PATH` e `SESSIONS_DB_PATH` no `config.py`.
- **WHEN** acessadas pelo backend.
- **THEN** elas devem apontar de forma determinística para `{ROOT_DIR}/data/mhw.db` e `{ROOT_DIR}/data/sessions.db` sem lógicas de busca secundária.

## Acceptance Criteria
- [ ] O backend inicia sem erros após a exclusão de `apps/backend/src/data`.
- [ ] Novas mensagens de chat são salvas no banco de dados da raiz (`data/sessions.db`).
- [ ] Consultas de monstros retornam dados do banco da raiz (`data/mhw.db`).
- [ ] Arquivos de log confirmam o carregamento dos XMLs a partir de `data/rag/`.
