# Change Proposal: Deep Research and Scalability Optimization

## Motivation
Recentemente, a arquitetura do projeto foi transicionada de um modelo monolítico para modular (monorepo). No entanto, resquícios da arquitetura antiga e redundâncias estruturais permanecem, criando o que chamamos de "gordura" no código e nos dados. Esta proposta visa realizar uma limpeza profunda, consolidar fontes de dados, padronizar importações e eliminar caminhos de fallback, resultando em uma codebase mais enxuta, eficiente e escalável.

## Scope
- **Backend (`apps/backend`)**: Limpeza de rotas, serviços e lógica de inicialização.
- **Data Management**: Consolidação das pastas de dados (`data/` vs `apps/backend/src/data/`).
- **Configuration (`core/config.py`)**: Remoção de hacks de path e lógica de fallback.
- **Project Root**: Organização de scripts de ferramentas e remoção de artefatos de build.

## New Capabilities
- **Single Source of Truth (SSoT)**: Centralização absoluta de dados RAG e bancos de dados SQLite.
- **Standardized Import Strategy**: Eliminação de `sys.path.insert` em favor de imports relativos ou configurados via PYTHONPATH/Entry points.
- **Unified Tooling**: Agrupamento de scripts de diagnóstico e utilitários em `tools/`.

## Impacted Capabilities
- **Data Loading**: A forma como o backend localiza o banco de dados e arquivos XML será simplificada.
- **Frontend Serving**: A lógica de servir os arquivos estáticos do Vite será fixada no caminho modular definitivo.
- **Project Structure**: Remoção de arquivos espalhados na raiz que não pertencem ao controle de versão ou deveriam estar em subpastas.

## Research Findings (Gordura Identificada)
1. **Redundância de Dados**: `apps/backend/src/data/` contém cópias de `data/` (root). Atualmente, o config aponta para o root, tornando a pasta dentro de `src` inútil.
2. **Path Hacks**: `main.py` e `config.py` tentam adivinhar caminhos para compatibilidade com a estrutura antiga.
3. **Templates Duplicados**: Existem pastas de templates em `apps/backend/` e `apps/backend/src/`.
4. **Scripts na Raiz**: `diagnostico.py` e outros utilitários poluem a raiz do projeto.
5. **Artefatos de Build**: Arquivos `.exe` e `.zip` na raiz não deveriam ser partilhados se o objetivo é um código modular limpo.
