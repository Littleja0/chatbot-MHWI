# Spec: chat-service (Tool Calling)

Definição das ferramentas de busca que serão expostas para a LLM.

## Requisitos de Ferramentas

### Requirement: Tool `search_equipment`
A ferramenta de busca deve aceitar os seguintes parâmetros:
- `query` (opcional): Nome parcial do equipamento ou monstro.
- `skills` (opcional): Lista de nomes de habilidades desejadas.
- `rank`: Filtrar por "LR", "HR", ou "MR" (obrigatório se detectado no contexto).
- `slot_min`: Nível mínimo de slot desejado em pelo menos uma peça.

### Requirement: Integração com Resposta
- O backend deve formatar o resultado do SQL em um JSON conciso para a LLM.
- A LLM deve usar esses dados para construir a resposta final, mantendo a personalidade do Gojo.

## Critérios de Aceitação
- **GIVEN** uma pergunta do usuário sobre builds de MR.
- **WHEN** a LLM chamar a ferramenta `search_equipment(rank="MR", skills=["Attack Boost"])`.
- **THEN** o sistema deve retornar JSON com as peças de MR que possuem a skill Attack Boost.
