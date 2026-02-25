# Spec: jewel-skill-description

## Overview

Exibição da descrição da skill que cada jóia concede, similar ao comportamento in-game de Monster Hunter World. Ao interagir com uma jóia equipada, o jogador vê o nome da jóia, as skills concedidas e uma descrição textual do efeito de cada skill.

## ADDED Requirements

### Requirement: Tooltip de Jóia Equipada

Ao passar o mouse sobre uma jóia equipada no slot, exibir tooltip com informações completas.

- **GIVEN** uma jóia está equipada em um slot de decoração
- **WHEN** o jogador passa o mouse (hover) sobre o slot da jóia
- **THEN** aparece um tooltip posicionado acima ou ao lado do slot
- **THEN** o tooltip mostra:
  - Nome da jóia (ex: "Joia de Ataque 1")
  - Para cada skill da jóia:
    - Nome da skill + nível concedido (ex: "Reforço de Ataque +1")
    - Descrição da skill (ex: "Um conjunto de skills básicas que aumentam o poder de ataque.")
- **THEN** o tooltip desaparece ao mover o mouse para fora do slot

### Requirement: Tooltip para Jóias com Múltiplas Skills

Jóias combo (ex: Expert+ Jewel 4) que concedem 2 skills mostram ambas.

- **GIVEN** uma jóia combo com 2 skills está equipada
- **WHEN** o jogador hover no slot
- **THEN** o tooltip lista ambas as skills com seus níveis e descrições separadamente

### Requirement: Backend Fornece Descrição da Skill

O endpoint `/equipment/decorations` deve incluir a descrição de cada skill concedida pela jóia.

- **GIVEN** o frontend chama GET `/equipment/decorations`
- **WHEN** o backend processa a requisição
- **THEN** cada objeto skill no array `skills` da jóia inclui o campo `description` com a descrição em português (fallback para inglês)

Formato de resposta atualizado:
```json
{
  "skills": [
    {
      "name": "Reforço de Ataque",
      "level": 1,
      "description": "Um conjunto de skills básicas que aumentam o poder de ataque."
    }
  ]
}
```

### Requirement: Descrição na Lista de Jóias (DecorationPicker)

Ao selecionar jóias no picker, cada item também mostra a descrição da skill.

- **GIVEN** o jogador abre o DecorationPicker para selecionar uma jóia
- **WHEN** visualiza a lista de jóias disponíveis
- **THEN** cada item mostra abaixo das skill tags uma linha de descrição da skill principal (truncada com `...` se muito longa)

### Requirement: Tooltip Estilizado

O tooltip deve seguir o design premium do Builder.

- **GIVEN** o tooltip de jóia aparece
- **THEN** tem fundo escuro com blur (glassmorphism)
- **THEN** borda com a cor do tier da jóia
- **THEN** animação suave de fade-in
- **THEN** posição automática (não sai da tela)
- **THEN** z-index acima de todos os outros elementos do Builder

## Interface Contract

### Backend Response Update

```python
# equipment.py - list_decorations
# Cada skill agora inclui "description"
skills.append({
    "name": skill_name,
    "level": d['skilltree_level'],
    "description": skill_description or ""
})
```

### Frontend Type Update

```typescript
// types/builder.ts - SkillRef
export interface SkillRef {
    name: string;
    level: number;
    description?: string;  // novo campo opcional
}
```

### CSS Classes

```
.deco-tooltip              — container do tooltip
.deco-tooltip__name        — nome da jóia
.deco-tooltip__skill       — bloco de skill
.deco-tooltip__skill-name  — nome + nível da skill
.deco-tooltip__skill-desc  — descrição da skill
```
