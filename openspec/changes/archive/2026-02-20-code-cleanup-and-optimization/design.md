# Design: Code Cleanup and Optimization

## Context
O projeto possui diversos arquivos legados de sessões de depuração e scripts de teste dispersos na raiz. A estrutura de diretórios em `apps/` está bem definida, mas a raiz precisa de uma limpeza para manter o padrão profissional do projeto.

## Goals
- Limpar a raiz do projeto de arquivos temporários e logs.
- Centralizar ferramentas de inspeção de dados em diretórios apropriados.
- Atualizar a documentação para refletir a estrutura organizacional correta.

## Design Decisions

### 1. Estratégia de Deleção (Trash)
Os seguintes arquivos serão removidos permanentemente, pois são logs de depuração gerados por ferramentas automáticas:
- `debug_output.txt`
- `debug_output_2.txt`
- `debug_output_2_tools.txt`
- `debug_output_3.txt`
- `debug_output_4.txt`
- `debug_output_5.txt`
- `debug_output_fixed.txt`
- `debug_output_no_tools.txt`

### 2. Estratégia de Migração (Tooling)
Scripts que ainda possuem valor para desenvolvimento serão movidos para a pasta `tools/`:
- `check_db.py` -> `tools/db/check_db.py`
- `check_armorset.py` -> `tools/db/check_armorset.py`
- `check_decorations.py` -> `tools/db/check_decorations.py`
- `check_skilltree.py` -> `tools/db/check_skilltree.py`
- `deep_inspect_skills.py` -> `tools/db/deep_inspect_skills.py`
- `find_attack_hybrids.py` -> `tools/db/find_attack_hybrids.py`
- `get_ids_for_prototype.py` -> `tools/db/get_ids_for_prototype.py`
- `inspect_crafting.py` -> `tools/db/inspect_crafting.py`

### 3. Consolidação de Backend
Arquivos como `test_naming.py` (atualmente aberto) devem ser movidos para a pasta de testes apropriada ou removidos se forem redundantes com o sistema de testes do FastAPI.

### 4. Atualização do README.md
O mapa da estrutura do projeto no `README.md` será atualizado para incluir a pasta `tools/` e remover referências a arquivos que não estarão mais na raiz.

## Risks / Trade-offs
- **Risco**: Um script movido pode ter caminhos relativos (hardcoded) para o banco de dados `mhw.db`.
- **Mitigação**: Revisar os scripts movidos e ajustar as referências de caminho se necessário.
- **Trade-off**: Perda de logs históricos de depuração, compensada por um sistema de arquivos muito mais limpo.
