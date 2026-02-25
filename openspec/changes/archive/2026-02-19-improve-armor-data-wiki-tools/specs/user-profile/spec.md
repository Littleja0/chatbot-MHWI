# Spec: user-profile (Integração de Rank e Joias)

Especificação de como o perfil do usuário influencia as buscas de ferramentas.

## Requisitos de Perfil

### Requirement: Filtragem Automática por Rank
- Se o usuário tem um Rank (MR) salvo no perfil, as ferramentas de busca devem priorizar ou restringir os resultados a esse Rank, a menos que o usuário peça explicitamente o contrário.

### Requirement: Sugestão de Joias (Decorations)
- Ao receber o resultado da busca de equipamentos (slots vazios), o bot deve verificar o inventário de joias do usuário (`user_jewels`) e sugerir quais equipar para maximizar a build.

## Critérios de Aceitação
- **GIVEN** um usuário com MR 5 e 2 joias de "Attack Boost".
- **WHEN** o bot sugere uma armadura com slots.
- **THEN** ele deve dizer explicitamente: "Encaixe suas 2 joias de Ataque nos slots nível 2 desta peça".
