# Spec: jewel-slot-visual

## Overview

Melhoria visual dos slots de jóia nos equipamentos do Builder. Quando uma jóia está equipada, o slot exibe um ícone que identifica visualmente qual jóia está no slot, ao invés de um losango genérico colorido.

## ADDED Requirements

### Requirement: Ícone Visual da Jóia Equipada

Quando uma jóia está equipada em um slot, o slot deve mostrar um identificador visual claro.

- **GIVEN** uma jóia está equipada em um slot de decoração de qualquer equipamento
- **WHEN** o jogador visualiza o slot no Builder
- **THEN** o slot exibe as iniciais da skill principal da jóia (ex: "At" para Reforço de Ataque)
- **THEN** o fundo do slot usa a cor correspondente ao tier da jóia (cinza T1, verde T2, azul T3, dourado T4)
- **THEN** a borda do slot fica sólida na cor do tier

### Requirement: Slot Vazio Mantém Visual Atual

Slots vazios continuam com o visual de losango transparente.

- **GIVEN** um slot de decoração está vazio
- **WHEN** o jogador visualiza o slot
- **THEN** o slot mostra o losango com opacidade reduzida na cor do tier do slot (comportamento atual)

### Requirement: Função de Abreviação de Skills

Uma função utilitária gera as iniciais da skill para exibição no slot.

- **GIVEN** o nome da skill é "Reforço de Ataque"
- **THEN** a abreviação é "At" (primeira letra da última palavra significativa)

- **GIVEN** o nome da skill é "Olho Crítico"
- **THEN** a abreviação é "OC" (primeira letra de cada palavra)

- **GIVEN** o nome da skill é "Exploração de Fraqueza"
- **THEN** a abreviação é "EF" (primeira letra de palavras significativas, ignorando "de")

Regras:
- Ignorar preposições: "de", "a", "do", "da", "em"
- Pegar a primeira letra de cada palavra significativa (até 3 caracteres)
- Se restar apenas 1 palavra, pegar as 2 primeiras letras

### Requirement: Diferenciação Visual Preenchido vs Vazio

O slot preenchido deve ser visualmente distinto do vazio de forma clara.

- **GIVEN** dois slots lado a lado, um preenchido e um vazio
- **WHEN** o jogador olha rapidamente
- **THEN** consegue distinguir imediatamente qual está preenchido (fundo sólido + texto) vs qual está vazio (losango transparente)

## Interface Contract

### Função: abbreviateSkill

```typescript
function abbreviateSkill(skillName: string): string
```

Localização: `utils/buildHelpers.ts` (novo arquivo)

### Alteração no EquipmentSlot.tsx

O slot preenchido renderizará:
```tsx
<span className="deco-slot__jewel-icon" style={{ borderColor, backgroundColor }}>
    <span className="deco-slot__jewel-abbr">{abbr}</span>
</span>
```

Ao invés do losango genérico atual.
