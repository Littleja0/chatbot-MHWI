# Spec: Clean Architecture & Modular Structure

## Requirements

### Requirement: Padronização de Paths
- **GIVEN** a estrutura monorepo atual (`apps/backend`, `apps/frontend`).
- **WHEN** os caminhos de base são calculados no `config.py`.
- **THEN** o `BASE_DIR` deve sempre referenciar `apps/backend` e o `ROOT_DIR` deve referenciar a raiz do projeto, usando `Path(__file__)` de forma robusta.

### Requirement: Limpeza de Imports
- **GIVEN** o uso de `sys.path.insert` no `main.py` e `config.py`.
- **WHEN** executando o backend em ambiente de desenvolvimento.
- **THEN** o código deve funcionar preferencialmente via estrutura de pacotes Python padrão, sem manipulação manual do `sys.path`, exceto para suporte a executável (frozen).

### Requirement: Centralização de Ferramentas
- **GIVEN** a presença de scripts de diagnóstico e build na raiz do projeto.
- **WHEN** a organização for aplicada.
- **THEN** esses scripts (`diagnostico.py`, `build.py`, etc.) devem ser movidos para a pasta `tools/`.

### Requirement: Servimento do Frontend
- **GIVEN** que o frontend é compilado em `apps/frontend/dist`.
- **WHEN** o servidor FastAPI é iniciado.
- **THEN** ele deve servir os arquivos estáticos a partir de `apps/frontend/dist` de forma fixa, removendo fallbacks para caminhos de arquitetura antiga.

## Acceptance Criteria
- [ ] O comando `python apps/backend/src/main.py` (ou equivalente modular) inicia o servidor com sucesso.
- [ ] A interface web carrega o frontend corretamente (servido pelo backend).
- [ ] Scripts em `tools/` continuam funcionando após a movimentação (verificar se dependem de caminhos relativos).
- [ ] Arquivos residuais (.exe, .spec, .zip) na raiz são limpos ou ignorados.
