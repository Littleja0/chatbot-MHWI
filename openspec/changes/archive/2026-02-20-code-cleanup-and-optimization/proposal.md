# Proposal: Code Cleanup and Optimization

## Contexto
O projeto Chatbot MHWI acumulou diversos arquivos temporários, scripts de teste pontuais e arquivos de log de depuração na raiz do diretório. Além disso, a estrutura real do projeto (`apps/backend`, `apps/frontend`) diverge levemente da documentação inicial, e há sinais de redundância em scripts de inspeção de dados. Esta mudança visa remover essa "gordura" para melhorar a manutenibilidade sem comprometer as funcionalidades existentes.

## Objetivos
- **Remoção de Arquivos Mortos**: Eliminar arquivos `.txt` de log/debug e scripts Python temporários que não fazem parte da aplicação principal.
- **Organização da Estrutura**: Mover ferramentas úteis para diretórios apropriados (`tools/`) e limpar a raiz do projeto.
- **Otimização Lógica**: Identificar e remover redundâncias no código-fonte, especialmente em scripts de tratamento de dados.
- **Consistência de Documentação**: Atualizar o README para refletir a estrutura atualizada.

## Impacted Capabilities
- `project-maintenance`: Consolidação e limpeza da estrutura de arquivos.
- `data-extraction-efficiency`: Verificação e otimização dos scripts de extração/inspeção dentro de `apps/backend/src`.

## Impact
- **Arquivos**: Deleção de múltiplos arquivos `debug_output*.py`, `check_*.py`, `inspect_*.py` na raiz.
- **Desenvolvimento**: Melhora na clareza do ambiente de desenvolvimento.
- **Performance**: Nenhuma mudança negativa esperada; possível ganho marginal em carregamento de módulos se houver imports redundantes removidos.

## Critérios de Sucesso
- Raiz do projeto limpa, contendo apenas arquivos essenciais (.env, requirements.txt, pastas estruturais).
- Chatbot continua funcionando perfeitamente (verificado via `run.bat`).
- Nenhum script essencial de extração de dados é perdido (movidos se necessários).
