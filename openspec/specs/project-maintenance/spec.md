# Spec: Project Maintenance Cleanup

## Overview
Esta especificação detalha a consolidação da raiz do projeto e a organização de ferramentas auxiliares para garantir um ambiente de desenvolvimento limpo e profissional.

## Requirements

### Requirement: Consolidação da Raiz (Root Cleanup)
A raiz do projeto deve conter apenas arquivos de configuração da infraestrutura e diretórios estruturais.
- **GIVEN** que o projeto possui arquivos `.txt` de log e scripts `.py` temporários na raiz.
- **WHEN** o comando de limpeza for executado.
- **THEN** todos os arquivos `debug_output*.txt` e scripts pontuais (ex: `check_*.py`, `inspect_*.py`, `find_*.py`) não essenciais devem ser removidos ou movidos para `tools/`.

### Requirement: Organização de Ferramentas (Tooling Organization)
Scripts que fornecem utilidades de suporte (inspeção de banco de dados, busca de IDs) devem ser centralizados.
- **GIVEN** a existência de scripts úteis como `check_db.py` ou `deep_inspect_skills.py`.
- **WHEN** a organização for aplicada.
- **THEN** esses scripts devem residir em `tools/` ou dentro de subdiretórios apropriados em `apps/backend`.

### Requirement: Integridade Funcional
A remoção de arquivos não deve afetar a execução do chatbot ou do backend.
- **GIVEN** o processo de limpeza.
- **WHEN** o `run.bat` for executado após a limpeza.
- **THEN** o sistema deve iniciar sem erros e todas as funcionalidades de chat e extração devem permanecer operais.
