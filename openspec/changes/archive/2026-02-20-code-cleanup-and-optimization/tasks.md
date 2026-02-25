# Tasks: Code Cleanup and Optimization

## Preparação e Revisão
- [x] 1.1 Criar diretório de destino `tools/db/` se não existir.
- [x] 1.2 Revisar scripts específicos (`check_db.py`, etc.) para identificar dependências de caminhos relativos.

## Limpeza de Arquivos Mortos
- [x] 2.1 Remover todos os arquivos `debug_output*.txt` da raiz do projeto.
- [x] 2.2 Remover scripts de busca rápida redundantes (`find_hybrids.py`, `find_decoration_mapping.py`, etc.) após confirmar que suas funcionalidades estão cobertas.

## Organização de Ferramentas
- [x] 3.1 Mover scripts de inspeção (`check_*.py`, `inspect_*.py`, `deep_inspect_*.py`, `get_ids_for_prototype.py`) para `tools/db/`.
- [x] 3.2 Ajustar os imports e caminhos de banco de dados nos scripts movidos para apontar corretamente para `../../data/mhw.db` (ou caminho equivalente).

## Consolidação de Backend
- [x] 4.1 Mover `test_naming.py` para `tests/` ou remover se for apenas um rascunho.
- [x] 4.2 Limpar arquivos de cache remanescentes (`__pycache__`) na raiz se houver.

## Documentação e Ajustes Finais
- [x] 5.1 Atualizar a seção "Estrutura do Projeto" no `README.md`.
- [x] 5.2 Verificar se o `run.bat` ainda funciona corretamente apontando para os locais corretos.

## Verificação de Integridade
- [x] 6.1 Executar o sistema via `run.bat` e realizar um teste de chat básico.
- [x] 6.2 Executar um dos scripts movidos em `tools/db/` para garantir que o acesso ao banco continua funcional.
