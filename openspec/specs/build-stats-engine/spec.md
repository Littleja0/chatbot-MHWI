# Spec: Build Stats Engine

## Purpose
Define o motor de cálculo de dano em tempo real (EFR), incluindo fórmulas de ataque efetivo, afinidade, multiplicadores de afiação, e suporte a customizações de armas Safi'jiiva, Kulve Taroth e Augmentações.

## Requirements

### Requirement: True Raw Calculation
O motor deve calcular o True Raw a partir do ataque base da arma, removendo o multiplicador de classe (bloat value).

#### Scenario: Calcular True Raw de Katana
- **GIVEN** uma Katana com Display Attack de 990 (bloat multiplier: 3.3x).
- **THEN** True Raw = 990 / 3.3 = 300.

### Requirement: Skill Bonuses na Estatística
O motor deve somar bônus de skills ofensivas ao True Raw e à Afinidade.

#### Scenario: Attack Boost Lv7
- **GIVEN** Attack Boost nível 7 ativo.
- **THEN** adicionar +21 True Raw E +5% Affinity ao cálculo.

#### Scenario: Critical Eye Lv7
- **GIVEN** Critical Eye nível 7 ativo.
- **THEN** adicionar +40% Affinity.

#### Scenario: Agitator Lv7 (Secret)
- **GIVEN** Agitator nível 7 ativo (requer Secret desbloqueado).
- **THEN** adicionar +28 True Raw e +20% Affinity (quando monstro enfurecido).

### Requirement: Sharpness Multiplier
O motor deve aplicar o multiplicador de afiação correto baseado na cor da barra.

#### Scenario: Multiplicadores por Cor
- **Red**: 0.50 | **Orange**: 0.75 | **Yellow**: 1.00 | **Green**: 1.05
- **Blue**: 1.20 | **White**: 1.32 | **Purple**: 1.39

### Requirement: Critical Damage Calculation
O motor deve considerar Critical Boost para ajustar o multiplicador de dano crítico.

#### Scenario: Sem Critical Boost
- **GIVEN** nenhum nível de Critical Boost.
- **THEN** multiplicador de crítico = 1.25.

#### Scenario: Critical Boost Lv3
- **GIVEN** Critical Boost nível 3.
- **THEN** multiplicador de crítico = 1.40.

### Requirement: EFR (Effective Raw) Final
Fórmula completa integrada.

#### Scenario: Build Endgame Completa
- **GIVEN** True Raw = 340, Sharpness = Purple (1.39), Affinity = 100%, Crit Boost Lv3 (1.40).
- **THEN** EFR = 340 * 1.39 * (1 + (1.0 * (1.40 - 1))) = 340 * 1.39 * 1.40 = **661.36 EFR**.

### Requirement: Safi'jiiva Awakening Stat Integration
Os despertares de Safi devem ser somados ao cálculo antes do EFR final.

#### Scenario: Attack Increase V (Safi)
- **GIVEN** um despertar "Attack Increase V" selecionado.
- **THEN** adicionar +15 True Raw ao cálculo.

#### Scenario: Sharpness Increase V (Safi)
- **GIVEN** um despertar "Sharpness Increase V" selecionado.
- **THEN** a barra de afiação deve ser estendida (mais unidades de Purple/White) e o multiplicador recalculado.

### Requirement: Kulve Taroth Custom Upgrade Integration
Os upgrades de Kulve (7 níveis) devem ser somados incrementalmente.

#### Scenario: Custom Upgrade Lv7 (Attack)
- **GIVEN** 7 níveis de Custom Upgrade focados em ataque aplicados.
- **THEN** o True Raw deve refletir o incremento total acumulado dos 7 níveis.

### Requirement: Augmentation Integration
Os aumentos padrão devem ser somados ao cálculo.

#### Scenario: Augment Attack Increase
- **GIVEN** um augment de "Attack Increase" aplicado.
- **THEN** adicionar +5 True Raw.

#### Scenario: Augment Affinity Increase
- **GIVEN** um augment de "Affinity Increase" aplicado.
- **THEN** adicionar +10% Affinity.

### Requirement: Elemental Damage Calculation
O motor deve calcular dano elemental separadamente.

#### Scenario: Elemento Ativo
- **GIVEN** uma arma com 600 Dragon element e Sharpness Purple.
- **THEN** Effective Elemental = (600 / 10) * 1.25 (purple elemental multiplier) = 75 Elemental EFR por hit.
