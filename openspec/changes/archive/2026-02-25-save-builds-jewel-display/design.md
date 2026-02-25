# Design: Save Builds & Jewel Display

## Context

O Build Builder atual (`BuilderView.tsx`) permite montar builds completas com arma, armaduras, amuleto, jóias, augments e Safi awakenings. O estado é gerenciado via `BuildContext` (useReducer). O `BuildExporter` permite enviar a build para o chat da IA. Porém, não há persistência de builds, e as jóias nos slots são renderizadas como losangos genéricos sem identificação visual.

A tabela `skilltree_text` no banco `mhw.db` já contém o campo `description` para cada skill, mas o endpoint `/equipment/decorations` não retorna essa informação.

## Goals / Non-Goals

### Goals
- Permitir salvar builds no localStorage com nome, timestamp e snapshot completo do `BuildState`
- UI intuitiva para listar, carregar, excluir e renomear builds salvas
- Trocar o visual dos slots de jóia: quando preenchido, mostrar o nome abreviado da skill ao invés de um losango genérico
- Ao hover sobre uma jóia equipada, exibir tooltip com nome da jóia, skills e descrições das skills
- Incluir a descrição da skill no endpoint de decorações

### Non-Goals
- Não implementar sync online / nuvem (apenas localStorage)
- Não implementar compartilhamento de builds via URL nesta change
- Não alterar a lógica de cálculo de stats

## Architecture

### 1. Saved Builds System

**Armazenamento**: `localStorage` com chave `mhwi-saved-builds`.

**Formato de dados**:
```typescript
interface SavedBuild {
    id: string;           // crypto.randomUUID()
    name: string;         // nome dado pelo jogador
    createdAt: string;    // ISO timestamp
    updatedAt: string;    // ISO timestamp
    buildState: BuildState;  // snapshot completo do estado
}
```

**Hook `useSavedBuilds`** (`hooks/useSavedBuilds.ts`):
- `savedBuilds: SavedBuild[]` — lista de builds salvas
- `saveBuild(name: string, state: BuildState): void` — salva uma nova build
- `loadBuild(id: string): BuildState` — retorna o estado para carregar
- `deleteBuild(id: string): void` — remove uma build
- `renameBuild(id: string, newName: string): void` — renomeia
- Internamente usa `useState` + `useEffect` para ler/escrever no localStorage
- Limite de 50 builds salvas (para evitar exceder o limite do localStorage)

**Nova action no BuildContext**: `LOAD_BUILD`
```typescript
{ type: 'LOAD_BUILD', payload: BuildState }
```
O reducer simplesmente substitui o estado inteiro pelo payload.

**UI — SavedBuildsPanel** (`components/builder/SavedBuildsPanel.tsx`):
- Painel colapsável no BuilderView, posicionado abaixo do `BuildExporter`
- Botão "💾 Salvar Build" abre um input para nome
- Lista de builds salvas com: nome, data, resumo (arma + EFR)
- Cada item tem botões de Carregar, Renomear e Excluir
- Ao carregar, exibe confirmação se a build atual tem equipamentos

### 2. Jewel Slot Visual Improvement

**Mudança no EquipmentSlot.tsx**:

Atualmente o slot de jóia renderiza:
```tsx
<span className="deco-slot__diamond" style={{ backgroundColor: TIER_COLORS[deco.tier] }} />
```

Será alterado para quando a jóia está equipada:
```tsx
<span className="deco-slot__jewel-icon" style={{ borderColor: TIER_COLORS[deco.tier] }}>
    <span className="deco-slot__jewel-abbr">{abbreviateSkill(deco.skill.name)}</span>
</span>
```

A função `abbreviateSkill` pegará as 2-3 primeiras letras do nome da skill:
- "Reforço de Ataque" → "At"
- "Olho Crítico" → "OC"
- "Exploração de Fraqueza" → "EF"

Lógica: primeira letra de cada palavra (até 3 letras), ou primeiras 2 letras se uma palavra só.

Visual: O slot preenchido terá um fundo colorido com base no tier, borda sólida e as iniciais centralizadas. Isso substitui o losango genérico.

**Tooltip com descrição da skill**: Ao hover, exibir uma tooltip custom (CSS puro) mostrando:
- Nome da jóia (ex: "Joia de Ataque 1")  
- Skill(s) concedida(s) com nível (ex: "Reforço de Ataque +1")
- Descrição da skill (ex: "Aumenta o poder de ataque.")

A tooltip será implementada com um `<div className="deco-tooltip">` que aparece via CSS `:hover` do container pai, usando `position: absolute`.

### 3. Backend — Descrição da Skill nas Decorações

**Alteração no endpoint `/equipment/decorations`** (`equipment.py`):

Substituir a chamada `_get_text` por uma query que traz o `description` junto:

```python
skill_row = conn.execute("""
    SELECT name, description FROM skilltree_text
    WHERE id = ? AND lang_id = 'pt'
""", (d['skilltree_id'],)).fetchone()
```

E incluir no resultado:
```python
skills.append({
    "name": skill_row['name'],
    "level": d['skilltree_level'],
    "description": skill_row['description'] or ""
})
```

O frontend receberá o campo `description` em cada skill da jóia e poderá renderizar no tooltip.

### 4. Mudanças nos Tipos (builder.ts)

```typescript
// Adicionar SavedBuild
export interface SavedBuild {
    id: string;
    name: string;
    createdAt: string;
    updatedAt: string;
    buildState: BuildState;
}

// Adicionar description na SkillRef (opcional)
export interface SkillRef {
    name: string;
    level: number;
    description?: string;  // novo campo opcional
}
```

## Key Decisions

1. **localStorage vs backend**: Implementar com localStorage mantém a feature 100% no frontend, sem criar endpoints novos de CRUD, sem precisar de autenticação e sem latência de rede. O limite de ~5MB do localStorage é mais que suficiente para 50 builds.

2. **Abreviação das skills nos slots**: Ao invés de usar ícones custom (que precisariam de assets para cada skill do jogo), usamos as iniciais da skill. Isso é mais leve e semanticamente claro.

3. **Tooltip CSS puro**: Usar CSS `:hover` ao invés de um sistema de tooltip com estado React. Mais simples, sem re-renders desnecessários. Funcionalidade adequada para desktop (hover).

4. **description como campo opcional em SkillRef**: Tornar description opcional evita quebrar interfaces existentes que já usam SkillRef sem esse campo.

5. **LOAD_BUILD como substituição total**: Ao carregar uma build, o reducer substitui todo o estado. Isso é mais simples do que dispatch individual para cada peça e garante consistência.

## Risks / Trade-offs

1. **localStorage pode ser limpo pelo browser**: Dados de builds salvas são locais e podem ser perdidos se o usuário limpar dados do browser. Futuro: considerar export/import de builds como arquivo JSON.

2. **Tooltip pode não funcionar bem em mobile**: Hover não existe em touchscreens. Alternativa futura: tap para abrir tooltip. Por agora, o builder é primariamente para desktop.

3. **Abreviação pode colidir**: Skills com nomes similares podem gerar as mesmas iniciais (ex: "Resistência a Fogo" e "Resistência a Água" ambos "RF" e "RA"). Mas como cada slot mostra uma jóia específica, o contexto + tooltip resolve qualquer ambiguidade.
