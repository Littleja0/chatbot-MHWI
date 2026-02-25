# Spec: Data Extraction Efficiency

## Overview
Esta especificação foca na manutenção da qualidade e performance dos scripts de extração e manipulação de dados localizados no backend.

## Requirements

### Requirement: Otimização de Scripts de Extração
Os scripts em `apps/backend/src` devem ser revisados para evitar redundância e garantir performance.
- **GIVEN** scripts de extração e parsing de dados.
- **WHEN** analisados para "gordura" lógica.
- **THEN** devem ser aplicadas melhorias de legibilidade e performance (ex: uso eficiente de conexões SQLite) sem alterar o output final (mhw.db).

### Requirement: Consistência de Dados
A limpeza não deve comprometer a base de dados gerada.
- **GIVEN** a execução do `extract_game_data.py`.
- **WHEN** finalizado após as otimizações.
- **THEN** o banco `mhw.db` resultante deve conter todos os dados necessários para o funcionamento das features de build e fraquezas.
