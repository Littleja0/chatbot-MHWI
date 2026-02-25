# Design: MHW Build Engine Optimization

## Context
A arquitetura atual do chatbot delega o cálculo de builds ao modelo de linguagem (LLM). Isso causa erros matemáticos e alucinações de slots. Este design introduz uma camada de validação determinística no backend para processar e otimizar builds usando dados reais do `mhw.db`.

## Goals
- Criar a função `calculate_and_validate_build` no `mhw_tools.py`.
- Integrar tabelas de Armor, Charms e Decorations do banco SQLite.
- Implementar um sistema de substituição de joias baseado em raridade e skills equivalentes.
- Fornecer um resumo técnico formatado para o LLM apresentar ao usuário.

## Architecture
O fluxo de dados funcionará da seguinte forma:
1. O LLM identifica as peças desejadas (Cabeça, Peito, etc.) e o Amuleto.
2. O sistema chama a ferramenta de validação.
3. A ferramenta busca os slots e skills nativas no banco.
4. O sistema preenche os slots com as joias "BiS" (Best in Slot) ideais.
5. Se a joia for Rarity 11/12, o sistema anexa as opções de "Substitutos".
6. O resultado retorna para o LLM, que apenas formata a resposta final com sua personalidade (Gojo).

### Database Schema mapping:
- **Armas/Armaduras:** Tabelas `wiki_armor` e `wiki_armor_skills`.
- **Amuletos:** Tabelas `charm` e `charm_skill`.
- **Joias:** Tabela `decoration` e `decoration_text` (filtrando por `skilltree_id`).
- **Set Bonus:** Tabela `armorset` e `armorset_bonus_skill`.

## Implementation Approach

### 1. Modelos de Dados (Data Classes)
- `ArmorPiece`: {name, slots, skills, set_id}
- `Jewel`: {name, slot_level, skill_points, rarity, is_hybrid}
- `BuildOutput`: {total_skills, active_bonuses, slots_usage, fragments}

### 2. A Função de Validação (`mhw_tools.py`)
```python
def validate_build(armor_names, weapon_name, charm_name):
    # 1. Fetch data for all pieces
    # 2. Identify available slots (e.g. [4, 4, 3, 1...])
    # 3. Fill slots starting from highest to lowest
    # 4. Sum skills and check caps
    # 5. Return JSON with validation report
```

### 3. Sistema de Substituição (Lookup Table)
Uma tabela interna no código mapeará joias raras para comuns:
- `Attack Jewel+ 4` -> `['Attack Jewel 1', 'Ironwall/Attack Jewel 4']`
- `Expert Jewel+ 4` -> `['Expert Jewel 1', 'Maintenance/Expert Jewel 4']`

## Risks / Trade-offs
- **Complexidade do SQLite:** Relacionar bônus de conjunto pode exigir queries complexas (JOINs triplos).
- **Variedade de Joias:** Existem centenas de joias híbridas; focaremos nas 10 mais importantes para combate (Ataque, Crítico, WEX, Agitador, etc).
