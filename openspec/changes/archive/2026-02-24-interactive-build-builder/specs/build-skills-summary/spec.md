# Spec: Build Skills Summary

## Purpose
Define o painel lateral de habilidades ativas, incluindo barras de progresso segmentadas com suporte a Dynamic Caps (Skill Secrets) e a seção de Set Bonuses.

## Requirements

### Requirement: Active Skills List
O painel deve exibir uma lista vertical de todas as skills ativas na build atual, ordenadas por nível (decrescente).

#### Scenario: Exibir Skill Ativa
- **GIVEN** uma build com Agitator Lv5 (3 de armadura + 2 de joias).
- **THEN** exibir "Agitador Lv5/5" com barra preenchida em 5/5 segmentos.
- **AND** indicar visualmente que a skill está no cap máximo (borda dourada ou ✓).

#### Scenario: Skill Abaixo do Cap
- **GIVEN** uma build com Critical Eye Lv4/7.
- **THEN** exibir "Olho Crítico Lv4/7" com barra preenchida em 4/7 segmentos.
- **AND** segmentos vazios devem ter cor diferente para indicar "pode subir mais".

### Requirement: Dynamic Skill Caps (Skill Secrets)
Skills que possuem "Secret" devem exibir barras adaptativas que mudam conforme set bonuses.

#### Scenario: Sem Secret Ativo
- **GIVEN** Agitator Lv5 SEM nenhum set bonus de Raging Brachydios.
- **THEN** a barra mostra 5 segmentos normais + 2 segmentos "trancados" (ícone de cadeado, cor escura/transparente).
- **AND** tooltip nos segmentos trancados: "Requer: Herança do Brachydios (2 peças)".

#### Scenario: Secret Ativo
- **GIVEN** Agitator Lv5 COM 2 peças de Raging Brachydios equipadas.
- **THEN** a barra expande para 7 segmentos totais. Os 5 primeiros são normais, os 2 extras têm borda brilhante (glow roxo/dourado) indicando que são "Secret levels".
- **AND** tooltip nos segmentos 6-7: "Desbloqueado por: Herança do Brachydios".

#### Scenario: Fatalis Universal Secret
- **GIVEN** 2 peças de Fatalis equipadas.
- **THEN** TODAS as skills com Secret disponível devem ter seus caps expandidos.
- **AND** a seção de Set Bonuses deve exibir "Traje de Fatalis Verdadeiro — Desbloqueia todos os segredos de skills".

#### Scenario: Safi Essence como Peça Virtual
- **GIVEN** 1 despertar "Teostra Essence" na arma Safi + 2 peças de armadura Teostra.
- **THEN** o sistema conta 3 peças totais de Teostra e ativa "Master's Touch" (requer 3 peças).

### Requirement: Skill Over-Cap Warning
Se uma skill excede seu cap (com ou sem secret), o sistema deve alertar visualmente.

#### Scenario: Skill Desperdiçada
- **GIVEN** Critical Eye Lv8 (cap máximo é 7, sem secret possível).
- **THEN** exibir "Olho Crítico Lv7/7 (+1 desperdiçado)" com segmento extra em VERMELHO.
- **AND** tooltip: "1 ponto desperdiçado. Considere trocar uma joia."

### Requirement: Set Bonuses Section
Uma seção dedicada abaixo das skills ativas mostrando set bonuses.

#### Scenario: Set Bonus Ativo
- **GIVEN** 3 peças de Teostra equipadas.
- **THEN** exibir card "Toque do Mestre (3/3 Teostra)" com ícone ✓ e descrição: "Ataques não reduzem afiação em acertos críticos."

#### Scenario: Set Bonus Parcial
- **GIVEN** 1 peça de Teostra equipada (precisa de 3).
- **THEN** exibir card "Toque do Mestre (1/3 Teostra)" em tom opaco/desativado.
- **AND** tooltip: "Equipe mais 2 peças para ativar."

#### Scenario: Múltiplos Sets
- **GIVEN** 2 peças Teostra + 2 peças Raging Brachydios + 1 peça genérica.
- **THEN** exibir ambos os set bonus cards com seus respectivos status.
