# Spec: RAG Verification Layer

## Purpose
Responsável por interceptar os resultados da busca semântica (RAG) e validar informações técnicas críticas contra o banco de dados estruturado (SQLite).

## Requirements

### Requirement: Extração de Entidades de Equipamento
- **GIVEN** uma string de contexto recuperada do RAG.
- **WHEN** processada para enriquecimento.
- **THEN** deve identificar via Regex nomes de Armaduras (ex: [Nome] α+/β+) e Armas que correspondam a entradas conhecidas no banco.

### Requirement: Enriquecimento de Dados via SQL
- **GIVEN** uma lista de nomes de equipamentos identificados.
- **WHEN** o serviço de chat prepara a mensagem.
- **THEN** deve executar `mhw_tools.get_armor_details` ou `get_weapon_details` para cada item para obter slots e skills reais.

### Requirement: Injeção de Seção de Dados Verificados
- **GIVEN** dados técnicos obtidos do banco de dados.
- **WHEN** montando o prompt final para a LLM.
- **THEN** deve criar um bloco separado chamado `DADOS TÉCNICOS VERIFICADOS (SQL)` contendo informações de Slots e Skills de base de cada peça citada.
