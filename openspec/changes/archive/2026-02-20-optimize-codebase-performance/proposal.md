<artifact id="proposal">
## Visão Geral
Esta mudança visa transformar o protótipo inicial em um sistema de alta qualidade e performance, eliminando o que chamamos de "gordura" (fat): dados hardcoded, scripts de teste redundantes e lógica acoplada. Atualmente, a engine utiliza dicionários internos para dados que já existem no banco de dados SQLite (`mhw.db`), o que é ineficiente e propenso a erros.

O objetivo é extrair a máxima performance através de consultas otimizadas ao DB e qualidade de código através de modularização e princípios SOLID.

## Impacto
- **`prototype_build_engine.py`**: Será refatorado para remover dados simulados e utilizar uma camada de serviço de dados.
- **Estrutura de Arquivos**: Remoção de arquivos de log/dump temporários (`model_test_out.txt`, etc) e organização de scripts utilitários.
- **Performance**: Redução do uso de memória e tempo de inicialização ao carregar dados sob demanda do banco de dados.

## Capacidades Afetadas
- **integração-banco-dados**: Transição total dos dados de armas, armaduras e joias para o SQLite.
- **motor-sugestao-otimizado**: Implementação de lógica de sugestão dinâmica (não baseada em if-else fixo).
- **limpeza-ambiente**: Remoção de redundâncias e scripts legados.

<success_criteria>
- 100% dos dados de jogo carregados via `mhw.db`.
- Código do motor reduzido em linhas (mantendo apenas lógica central).
- Tempo de resposta para sugestões de builds inferior a 10ms.
- Projeto pronto para escala sem carregar dados pesados em memória global.
</success_criteria>
</artifact>
