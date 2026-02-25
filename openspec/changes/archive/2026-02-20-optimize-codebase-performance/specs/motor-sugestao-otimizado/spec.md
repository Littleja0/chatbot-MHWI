<artifact id="spec">
# Especificação: Motor de Sugestão Otimizado

## Objetivo
Implementar a lógica central de recomendação de equipamentos e joias de forma dinâmica, removendo estruturas de controle rígidas e permitindo maior flexibilidade.

## Requisitos Detalhados

### Requisito: Lógica de Pontuação (Scoring)
- **DADO QUE** existem várias joias que se encaixam em um slot
- **QUANDO** o motor precisar escolher a melhor
- **ENTÃO** ele deve aplicar uma fórmula de pontuação baseada em: `Prioridade da Skill * Nível da Skill * (1 / Raridade)`.

### Requisito: Desacoplamento de Equipamentos
- **DADO QUE** novas armaduras podem ser adicionadas ao banco de dados
- **QUANDO** a engine processar uma build
- **ENTÃO** ela deve iterar sobre a lista de slots sem conhecer previamente os nomes das armaduras (lógica genérica).

### Requisito: Tratamento de Slots Híbridos
- **DADO QUE** existem joias de nível 4 que concedem duas skills
- **QUANDO** o sistema buscar o "Ideal"
- **ENTÃO** o motor deve ser capaz de avaliar se uma joia híbrida supre melhor a necessidade total da build do que duas joias simples.

## Critérios de Aceite
- Remoção total de `if piece['name'] == '...'` ou similar.
- O motor deve aceitar uma lista de "Prioridades" (ex: Ataque > Crítico) para guiar as sugestões.
</artifact>
