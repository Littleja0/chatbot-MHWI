# Spec: Jewel Substitution Capacity

## Overview
Esta especificação define a lógica de substituição de joias por versões mais acessíveis (RNG Friendly), permitindo que o sistema ofereça alternativas funcionais enquanto o usuário não possui as joias ideais (BiS - Best in Slot).

## Requirements

### Requirement: Mapeamento de Joias BiS vs Substitutos
- **AS A** Sistema de Recomendação
- **I WANT TO** Ter um mapeamento de joias de raridade 11/12 (ex: Attack 4, Expert 4) para suas versões de raridade 6/7 (Ataque 1, Expert 1) ou versões híbridas de raridade 10.
- **THEN** Permitir que o chatbot apresente as duas opções ao usuário.

### Requirement: Sugestão de Joias Híbridas
- **AS A** Assistente Útil
- **I WANT TO** Sugerir joias que combinam a habilidade principal com uma secundária utilitária (ex: Ironwall/Attack Jewel 4).
- **THEN** Ajudar o usuário a preencher os slots de nível 4 enquanto ele não possui as joias puras.

## User Scenarios

### Scenario: Sugestão de Alternativa para Ataque+ 4
- **GIVEN** O chatbot sugere uma build ideal que usa `Attack Jewel+ 4`.
- **WHEN** O sistema gera a resposta final.
- **THEN** Deve incluir uma nota: "Caso não tenha Attack 4, você pode usar uma Attack Jewel 1 (Slot 1) ou uma Ironwall/Attack Jewel 4 (Slot 4)."

### Scenario: Priorização de Joias Híbridas Comuns
- **GIVEN** Um slot de nível 4 vazio e a necessidade de `Critical Eye`.
- **WHEN** O usuário é iniciante no Master Rank.
- **THEN** Sugerir joias como `Maintenance/Expert Jewel 4` antes de exigir joias de raridade 12.
