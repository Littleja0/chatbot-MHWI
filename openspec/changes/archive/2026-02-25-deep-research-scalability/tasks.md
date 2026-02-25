# Tasks: Codebase Cleanup and Scalability Optimization

Breakdown of implementation tasks to achieve a clean modular architecture.

## 1. Preparation & Safety
- [x] 1.1 Criar backup de `data/mhw.db` e `data/sessions.db` antes de qualquer remoção.
- [x] 1.2 Validar que o conteúdo de `data/` (root) está sincronizado com `apps/backend/src/data/`.

## 2. Data Consolidation (SSoT)
- [x] 2.1 Remover diretório redundante `apps/backend/src/data/`.
- [x] 2.2 Garantir que `apps/backend/src/data/mhw.db` (caso exista diferente do root) seja removido.
- [x] 2.3 Remover `apps/backend/src/data/rag/` e validar que os XMLs estão apenas em `data/rag/`.

## 3. Core Refactoring (Backend)
- [x] 3.1 Refatorar `apps/backend/src/core/config.py`:
    - Simplificar cálculo de `BASE_DIR` e `ROOT_DIR`.
    - Apontar `MHW_DB_PATH` e `SESSIONS_DB_PATH` definitivamente para a raiz.
    - Remover lógicas de fallback de path de dados.
- [x] 3.2 Refatorar `apps/backend/src/main.py`:
    - Remover injeções de `sys.path`.
    - Fixar caminho de servimento do frontend para `apps/frontend/dist`.
- [x] 3.3 Consolidar templates HTML em `apps/backend/templates/` e remover duplicatas em `src/`.

## 4. Project Reorganization (Tooling)
- [x] 4.1 Mover `diagnostico.py` e `diagnostico_categorias.py` para `tools/`.
- [x] 4.2 Mover `build.py`, `build_manifest.py` (se existir) e `updater.py` para `tools/`.
- [x] 4.3 Atualizar `run.bat` para refletir os novos caminhos dos scripts.
- [x] 4.4 Atualizar `MHWChatbot.spec` para refletir a nova estrutura de pastas no build do PyInstaller.

## 5. Final Verification
- [x] 5.1 Executar backend em modo de desenvolvimento e testar chat/RAG.
- [x] 5.2 Executar diagnósticos em `tools/` para verificar integridade.
- [x] 5.3 Simular um processo de build para validar que não há caminhos quebrados.
- [x] 5.4 Remover arquivos órfãos na raiz (`.exe`, `.zip`, `.spec.backup`).
