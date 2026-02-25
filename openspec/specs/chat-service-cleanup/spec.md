# Spec: Chat Service Cleanup

## Purpose
Responsável por gerenciar a construção do prompt do sistema e a integração com as configurações do usuário no `sessions.db`.

## Requirements

### Requirement: Remover Dependência de Joias
- **GIVEN** que um chat está sendo processado.
- **WHEN** o `anti_hallucination_middleware` é executado.
- **THEN** ele NÃO deve buscar a chave `jewels` nas configurações do usuário nem incluí-la no prompt.

### Requirement: Limpeza Automática do Banco de Sessões
- **GIVEN** que o sistema foi atualizado para esta versão.
- **WHEN** o backend for iniciado ou durante a primeira mensagem do usuário.
- **THEN** a entrada `jewels` na tabela `user_config` deve ser deletada para todos os usuários/instâncias para evitar dispersão de dados obsoletos.

### Requirement: Restrição de Prompt "Lei Seca"
- **GIVEN** a construção do `system_instruction`.
- **WHEN** a personalidade do Gojo é injetada.
- **THEN** deve ser incluída uma regra mandatória que proíbe o preenchimento de lacunas técnicas (slots e skills) caso os dados verificados não estejam presentes.
