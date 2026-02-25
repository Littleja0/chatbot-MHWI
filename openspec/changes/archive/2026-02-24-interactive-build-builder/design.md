# Design: Interactive Build Builder

## Contexto

O MHW:I Chatbot possui um frontend em React/Vite/TypeScript e um backend em FastAPI/Python com banco SQLite (`mhw.db`). O Header já possui abas inativas ("Builds", "Monsters", "Guides"). Esta change ativa a aba "Builds" e implementa um construtor de builds interativo com cálculo de dano em tempo real.

## Goals / Non-Goals

### Goals
- Implementar uma view de Builder completa com seleção visual de equipamento.
- Calcular EFR (Effective Raw) em tempo real no frontend.
- Validar encaixe de joias por tier (1-4) com feedback visual claro.
- Suportar Dynamic Caps (Skill Secrets) e Set Bonuses.
- Suportar customização profunda de armas (Safi Awakenings, Kulve Custom Upgrades, Augmentations).
- Integrar Builder ↔ Chat (exportar build para o Gojo analisar).

### Non-Goals
- Otimização automática de builds (solver/optimizer) — isso é uma feature futura.
- Importação de builds de sites externos (Honey Hunter, etc).
- Edição do banco de dados (mhw.db é read-only).

## Arquitetura

### Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                        App.tsx                          │
│  ┌─────────┐  ┌────────────────────────────────────┐    │
│  │ Sidebar │  │ Main Area                          │    │
│  │         │  │  ┌──────────────────────────────┐  │    │
│  │ (chats) │  │  │ Header (Tabs)                │  │    │
│  │         │  │  │ [Chat] [BUILDS] [Monsters]   │  │    │
│  │         │  │  └──────────────────────────────┘  │    │
│  │         │  │                                    │    │
│  │         │  │  ┌──── activeTab === "builds" ──┐  │    │
│  │         │  │  │                              │  │    │
│  │         │  │  │  ┌────────┐ ┌─────────────┐  │  │    │
│  │         │  │  │  │Equip   │ │ Summary     │  │  │    │
│  │         │  │  │  │Grid    │ │ Cards       │  │  │    │
│  │         │  │  │  │        │ │ (Skills +   │  │  │    │
│  │         │  │  │  │+ Decos │ │  Stats)     │  │  │    │
│  │         │  │  │  │+ Weapon│ │             │  │  │    │
│  │         │  │  │  │ Custom │ │             │  │  │    │
│  │         │  │  │  └────────┘ └─────────────┘  │  │    │
│  │         │  │  │                              │  │    │
│  │         │  │  └──────────────────────────────┘  │    │
│  └─────────┘  └────────────────────────────────────┘    │
│                                                         │
│  Providers: ChatProvider + BuildProvider                 │
└─────────────────────────────────────────────────────────┘
```

### Decisão: Tab Navigation no App.tsx

O `Header.tsx` atual renderiza tabs estáticas sem funcionalidade. A decisão é:
- Adicionar um estado `activeTab` no `App.tsx` (não no contexto, pois é puramente UI).
- O `Header` recebe `activeTab` e `onTabChange` como props.
- O `AppLayout` renderiza condicionalmente `ChatArea` ou `BuilderView` com base no `activeTab`.
- O `Sidebar` permanece visível em ambas as views (mas pode ser contextual no futuro).

### Decisão: BuildContext separado do ChatContext

O estado da build é complexo e independente do chat. Criar um `BuildContext` dedicado:

```typescript
// contexts/BuildContext.tsx
interface BuildState {
  weapon: WeaponSlot | null;
  armor: Record<ArmorType, ArmorSlot | null>;  // head, chest, arms, waist, legs
  charm: CharmSlot | null;
  decorations: Record<string, DecorationSlot[]>; // keyed by equipment piece id
  weaponAugments: Augment[];
  weaponCustomUpgrades: CustomUpgrade[];
  safiAwakenings: SafiAwakening[];
}

interface ComputedStats {
  trueRaw: number;
  displayAttack: number;
  affinity: number;
  efr: number;
  elementDamage: number;
  defense: number;
  activeSkills: SkillLevel[];     // skills com nível atual
  activeSetBonuses: SetBonus[];   // set bonuses ativos
  skillSecrets: string[];         // quais secrets estão desbloqueados
}
```

**Rationale**: Manter separado do `ChatContext` evita re-renders desnecessários no chat quando o usuário ajusta uma joia no builder (e vice-versa).

### Decisão: Engine de Cálculo no Frontend

O cálculo de EFR será feito inteiramente no frontend (TypeScript) por razões de UX:
- **Feedback instantâneo**: O usuário vê o número mudando sem esperar uma request.
- **Sem carga no backend**: O servidor não precisa processar cálculos matemáticos simples.

#### Fórmulas Implementadas

```
True Raw = (Base Attack / Weapon Class Multiplier)
         + Skill Bonuses (Attack Boost, Agitator, etc.)
         + Augment Bonuses
         + Safi/Kulve Bonuses

Effective Affinity = Base Affinity
                   + Skill Bonuses (Critical Eye, Agitator, WEX, etc.)

Sharpness Multiplier = Lookup table por cor de afiação
  (Red: 0.50, Orange: 0.75, Yellow: 1.00, Green: 1.05, Blue: 1.20, White: 1.32, Purple: 1.39)

Critical Damage Multiplier = 1.25 (base)
  + Critical Boost bonus (Lv1: 1.30, Lv2: 1.35, Lv3: 1.40)

EFR = True Raw * Sharpness Multiplier * (1 + (Affinity/100 * (Crit Multiplier - 1)))
```

### Decisão: Lógica de Joias (Tier Filtering)

A validação de joias é uma regra simples do tipo "cabe ou não cabe":

```typescript
function canInsertDecoration(slotTier: number, decoTier: number): boolean {
  return slotTier >= decoTier;
}
```

O frontend filtra a lista de joias disponíveis baseado no tier do slot clicado. Se o slot é tier 3, a lista mostra apenas joias de tier 1, 2 e 3.

### Decisão: Dynamic Caps (Skill Secrets)

O frontend precisa de um mapeamento estático de "set bonus → skills desbloqueadas":

```typescript
const SKILL_SECRETS: Record<string, { pieces: number; unlockedSkills: string[] }[]> = {
  "Raging Brachydios":  [{ pieces: 2, unlockedSkills: ["Agitator"] }],
  "Gold Rathian":       [{ pieces: 2, unlockedSkills: ["Divine Blessing"] }],
  "Zorah Magdaros MR":  [{ pieces: 3, unlockedSkills: ["Artillery"] }],
  "Fatalis":            [{ pieces: 2, unlockedSkills: ["ALL"] }],  // Desbloqueia TODOS
  // ...
};
```

Quando o usuário equipa N peças de um set, o `ComputedStats` verifica quais secrets estão ativos e ajusta o `maxLevel` de cada skill na UI.

**Essências de Safi'jiiva** contam como +1 peça do set correspondente (ex: "Teostra Essence" = +1 peça Teostra para ativar "Master's Touch" com apenas 2 peças reais).

### Decisão: Customização de Armas (Safi/Kulve/Augments)

#### Safi'jiiva Awakenings
- 5 slots de despertar por arma.
- Cada slot pode ser: Stat boost (Attack I-VI, Sharpness I-VI, Affinity I-VI), Slot upgrade, Set Bonus Essence, ou Skill.
- Os valores são hardcoded em uma tabela de lookup no frontend.

#### Kulve Taroth Custom Upgrades
- 7 níveis de upgrade incremental (Attack, Affinity, Element, Defense).
- Apenas armas "customizáveis" (Taroth weapons, não Kjarr).
- Kjarr weapons possuem skill embutida ("Critical Element" ou "Critical Status") que é adicionada automaticamente.

#### General Augmentations
- O número de slots de augment depende da raridade da arma (R10: 5 slots, R11: 4 slots, R12: 3 slots).
- Cada augment tem custo em slots (1-3) e efeito fixo.

### Novos Endpoints (Backend)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/equipment/weapons` | GET | Lista todas as armas, com filtros por tipo e elemento. Retorna slots, ataque, afinidade, elemento. |
| `/equipment/armor` | GET | Lista todas as armaduras, com filtros por rank e tipo. Retorna slots e skills. |
| `/equipment/decorations` | GET | Lista todas as joias com tier e skills. |
| `/equipment/set-bonuses` | GET | Lista todos os set bonuses com peças necessárias e efeitos. |
| `/equipment/charms` | GET | Lista todos os amuletos com skills e níveis. |

Todos os endpoints retornam dados em português (lang_id='pt') com fallback para inglês.

### Novos Componentes (Frontend)

| Componente | Responsabilidade |
|------------|-----------------|
| `BuilderView.tsx` | Layout principal da aba Builds (grid + summary) |
| `EquipmentSlot.tsx` | Card clicável para cada peça de equipamento |
| `EquipmentPicker.tsx` | Modal/dropdown para selecionar equipamento |
| `DecorationPicker.tsx` | Modal para selecionar joias (filtrado por tier) |
| `WeaponCustomizer.tsx` | Painel de Safi/Kulve/Augments |
| `SkillBar.tsx` | Barra segmentada de skill com suporte a Secret levels |
| `StatsPanel.tsx` | Painel de Combat Stats (EFR, Affinity, Element) |
| `SetBonusCard.tsx` | Card mostrando set bonuses ativos e peças faltando |
| `BuildExporter.tsx` | Botão para exportar build para o Chat |

### Fluxo de Dados

```
Usuário clica em slot → EquipmentPicker abre
  → Fetch /equipment/armor?type=head (ou cache local)
  → Usuário seleciona peça → dispatch("setArmor", { slot: "head", piece })
  → BuildContext recalcula ComputedStats
  → SkillBar, StatsPanel, SetBonusCard re-renderizam
  → Se skill > cap normal MAS secret ativo → barra expande
  → Se skill > cap (mesmo secret) → alerta visual de desperdício
```

## Risks / Trade-offs

- **Dados Hardcoded de Safi/Augments**: Os despertares de Safi e valores de augment não existem no mhw.db de forma estruturada. Precisaremos de tabelas de lookup hardcoded no frontend. Risco: manutenção manual se dados mudarem.
- **Performance**: Se o mhw.db tiver centenas de armas, o fetch inicial pode ser pesado. Mitigação: paginação nos endpoints e cache no frontend via `useState` + `useMemo`.
- **Complexidade do EFR**: A fórmula de dano do MHW é documentada pela comunidade mas tem edge cases (Power Charm, Talon, Canteen buffs). Decisão: implementar a versão "sheet" (sem buffs temporários) e adicionar buffs opcionais em iteração futura.
