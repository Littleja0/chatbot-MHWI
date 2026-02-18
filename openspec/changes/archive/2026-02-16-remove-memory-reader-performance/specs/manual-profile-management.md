# Spec: manual-profile-management

## ADDED Requirements

### Requirement: Atualização Manual de Perfil
As informações de MR (Master Rank) e HR (Hunter Rank) devem ser lidas exclusivamente do `sessions.db`.

#### Scenario: Consulta de Build
- **WHEN** O usuário pede uma build.
- **THEN** A IA deve usar o MR registrado no banco de dados para filtrar equipamentos, em vez de tentar ler o MR vivo da memória.

### Requirement: Remoção de Sincronização Automática
O sistema deve remover qualquer chamada ou botão que sugira "Auto-sync" ou "Memory Connect".

#### Scenario: Visualização do Perfil
- **WHEN** O usuário acessa a rota `/user/profile`.
- **THEN** Os dados retornados devem ser apenas os persistidos, sem tentativa de refresh via memória.
