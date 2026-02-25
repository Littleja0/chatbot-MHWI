# Spec: build-equipment-grid (delta)

## Overview

Alterações no componente `EquipmentSlot` para suportar o novo visual de jóias e tooltips. Esta é uma modificação da capability existente `build-equipment-grid`.

## CHANGED Requirements

### Requirement: Renderização de Slots de Jóia Atualizada

O componente `EquipmentSlot` deve usar o novo componente visual para jóias preenchidas.

- **GIVEN** o componente `EquipmentSlot` renderiza slots de decoração
- **WHEN** um slot tem uma jóia equipada
- **THEN** renderiza o novo visual com iniciais da skill (import de `jewel-slot-visual`)
- **THEN** adiciona o tooltip de hover com descrição (import de `jewel-skill-description`)
- **THEN** mantém o comportamento de clique direito para remover

### Requirement: Slots com Tooltip Não Interferem no Layout

Os tooltips de jóias não devem afetar o layout do EquipmentSlot.

- **GIVEN** o jogador hover sobre um slot de jóia em um equipamento
- **WHEN** o tooltip aparece
- **THEN** o tooltip usa `position: absolute` e não empurra outros elementos
- **THEN** o tooltip é renderizado dentro do `deco-slot` button com overflow visible

### Requirement: Dados da Jóia para Tooltip

O `EquipmentSlot` precisa receber os dados completos da jóia (incluindo descrição) para renderizar o tooltip.

- **GIVEN** o `BuilderView` passa a prop `decorations` para o `EquipmentSlot`
- **WHEN** as jóias incluem o campo `description` nas skills
- **THEN** o `EquipmentSlot` pode renderizar o tooltip com a descrição
- **THEN** se `description` não estiver presente (fallback), o tooltip mostra apenas nome e nível

## Interface Contract

### Props do EquipmentSlot (sem mudança na interface)

As props existentes (`decorations?: (any | null)[]`) já suportam os dados adicionais, pois o campo `description` é incluído dentro dos objetos de skill das decorações.

### CSS Additions ao Builder.css

Novas classes CSS adicionadas ao `Builder.css`:
- `.deco-slot__jewel-icon` — container do ícone visual (substitui diamond quando preenchido)
- `.deco-slot__jewel-abbr` — texto das iniciais
- `.deco-tooltip` — container do tooltip
- `.deco-tooltip__*` — sub-elementos do tooltip
