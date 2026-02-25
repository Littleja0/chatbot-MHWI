<artifact id="spec">
# Especificação: Integração com Banco de Dados

## Objetivo
Estabelecer uma camada de acesso a dados robusta e performática para consultar o banco de dados `mhw.db`, substituindo dados hardcoded por consultas dinâmicas.

## Requisitos Detalhados

### Requisito: Gerenciador de Banco de Dados Único
- **DADO QUE** a aplicação precisa acessar informações de equipamentos ou joias
- **QUANDO** o `DatabaseManager` for instanciado
- **ENTÃO** ele deve manter uma conexão única (ou pool) com o arquivo `d:\chatbot MHWI\data\mhw.db` para evitar overhead de abertura de arquivos.

### Requisito: Consulta de Joias por Slot e Skill
- **DADO QUE** o motor de build identifica um slot vazio de nível `N`
- **QUANDO** solicitar sugestões de joias para uma skill `S`
- **ENTÃO** o sistema deve retornar apenas joias cujo nível seja `<=` `N` e que possuam a skill `S`, ordenadas por raridade decrescente.

### Requisito: Performance de Consulta
- **DADO QUE** múltiplas consultas podem ser feitas durante a geração de uma build
- **QUANDO** uma query SQL for executada
- **ENTÃO** o tempo de resposta do banco de dados deve ser inferior a 5ms por consulta simples.

### Requisito: Abstração de Entidades
- **DADO QUE** os dados retornados do SQLite são tuplas/listas puras
- **QUANDO** os dados chegarem à camada de negócio
- **ENTÃO** eles devem ser convertidos em objetos de domínio (ex: dataclasses em Python) para facilitar a manutenção.

## Critérios de Aceite
- Nenhuma string de conexão ou caminho de banco de dados deve estar espalhado pelo código (usar configuração central).
- O arquivo original `prototype_build_engine.py` não deve conter mais o dicionário `decorations`.
</artifact>
