# Design: Modular Architecture Scalability & Efficiency

## Goal
O objetivo deste design é eliminar redundâncias técnicas e estruturais introduzidas durante a migração para a arquitetura modular, estabelecendo uma "Fonte Única de Verdade" (SSoT) para dados e simplificando a resolução de caminhos (paths) no backend.

## Technical Decisions

### 1. Consolidação de Dados (SSoT)
- **Decisão**: Remover a pasta `apps/backend/src/data/` e todas as suas subpastas.
- **Racional**: Os arquivos `mhw.db`, `sessions.db` e os XMLs do RAG já residem em `data/` na raiz do projeto. O código em `core/config.py` já aponta para a raiz como prioridade. Manter cópias dentro do `src` gera confusão e risco de inconsistência.

### 2. Padronização de Templates
- **Decisão**: Consolidar todos os arquivos `.html` (splash, overlay) em `apps/backend/templates/`.
- **Racional**: Atualmente existem templates espalhados entre `src/` e o nível superior do app. Centralizar na pasta de templates padrão facilita a manutenção.

### 3. Simplificação de Resolução de Paths (`config.py`)
- **Decisão**: Refatorar `apps/backend/src/core/config.py` para usar caminhos absolutos baseados na localização do arquivo, sem lógicas de "fallback" (ex: "tenta aqui, se não der tenta ali").
- **Implementação**:
  ```python
  BASE_DIR = Path(__file__).resolve().parent.parent.parent # apps/backend
  ROOT_DIR = BASE_DIR.parent.parent                        # project root
  DATA_DIR = ROOT_DIR / "data"
  ```

### 4. Limpeza do Entry Point (`main.py`)
- **Decisão**: Remover as injeções manuais no `sys.path`.
- **Racional**: Se o projeto for executado corretamente (via módulo ou com o diretório correto no PYTHONPATH), essas injeções são desnecessárias e poluem o código. Manteremos apenas o estritamente necessário para o modo "frozen" (PyInstaller).

### 5. Organização de Ferramentas (Tooling)
- **Decisão**: Mover scripts utilitários da raiz para a pasta `tools/`.
- **Arquivos**: `diagnostico.py`, `diagnostico_categorias.py`, `build.py`, `updater.py`.

## Implementation Strategy
1. Backup de arquivos críticos (DBs).
2. Remoção física dos diretórios redundantes.
3. Atualização do `config.py` para as novas definições de path.
4. Teste de inicialização do backend para garantir que o RAG e o banco de dados são localizados corretamente.
5. Teste de build para garantir que a nova estrutura não quebre o empacotamento.

## Risks / Trade-offs
- **Risco**: Quebra de caminhos relativos em scripts de terceiros ou ferramentas de build.
- **Mitigação**: Atualizar o arquivo `.spec` (PyInstaller) e o `run.bat` simultaneamente às mudanças de diretório.
