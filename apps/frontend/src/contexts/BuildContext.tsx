import React, { createContext, useContext, useReducer, useMemo, ReactNode } from 'react';
import {
    BuildState,
    ComputedStats,
    WeaponSlot,
    ArmorSlot,
    ArmorType,
    CharmSlot,
    DecorationSlot,
    Augment,
    SafiAwakening,
    CustomUpgrade,
    SkillLevel,
    SetBonus,
    SkillRef,
} from '../types/builder';
import { calculateTrueRaw, calculateAffinity, calculateEFR, calculateElementalEFR } from '../utils/calcEngine';
import { WEAPON_MULTIPLIERS } from '../data/weaponMultipliers';
import { SKILL_SECRETS, SKILL_SECRET_MAX_LEVELS } from '../data/skillSecrets';
import { SKILL_BONUSES } from '../data/skillBonuses';

// Max levels from DB (PT names)
const SKILL_MAX_LEVELS: Record<string, number> = {
    'Reforço de Ataque': 7, 'Olho Crítico': 7, 'Exploração de Fraqueza': 3,
    'Reforço Crítico': 3, 'Agitador': 7, 'Desempenho Máximo': 3,
    'Indignação': 5, 'Coalescência': 3, 'Heroísmo': 7, 'Fortificar': 1,
    'Reforço Não Elemental': 1, 'Bloqueio Ofensivo': 3, 'Poder Máximo': 5,
    'Poder Latente': 7, 'Artesanato': 5, 'Artilharia': 5,
    'Ataque de Fogo': 6, 'Ataque de Água': 6, 'Ataque de Raio': 6,
    'Ataque de Gelo': 6, 'Ataque de Dragão': 6,
    'Bênção Divina': 5, 'Reforço de Vida': 3, 'Reforço de Defesa': 7,
    'Foco': 3, 'Mais Munição/Elemento': 3, 'Resistência Atordoamento': 3,
    'Tempo de Esquiva': 5, 'Constituição': 5, 'Pele de Ferro': 3,
    'Reforço de Selo Ancião': 1, 'Afiação Rápida': 3, 'Bainha Rápida': 3,
    'Quebra-parte': 3, 'Perícia em Ferramentas': 5, 'Maratonista': 3,
    'Ladrão de Vigor': 5, 'Bombardeiro': 5, 'Atordoante': 5,
    'Prolongar Poder': 3, 'Prolongar Item': 3, 'Bloqueio': 5,
    'Sem Recuo': 3, 'Antivento': 5, 'Sobrevivente': 3,
    'Disparos Normais': 2, 'Disparos Perfurantes': 2, 'Disparo Potente/Disperso': 2,
    'Surto de Vigor': 3, 'Maestro de Sonoro': 2, 'Saque Crítico': 3,
    'Reforço Munição Especial': 2, 'Mobilidade Aquática/Polar': 3,
    'Extensor de Esquiva': 3, 'Tampões': 5, 'Alcance Amplo': 5,
    'Furtividade': 3, 'Intimidação': 3, 'Cogumelaria': 3,
    'Resistência a Veneno': 3, 'Resistência a Paralisia': 3,
    'Resistência a Sono': 3, 'Resistência a Explosão': 3,
    'Resistência a Fogo': 3, 'Resistência a Água': 3,
    'Resistência a Raio': 3, 'Resistência a Gelo': 3, 'Resistência a Dragão': 3,
    'Resistência a Tremor': 3, 'Resistência Sangramento': 3,
    'Resistência a Eflúvios': 3, 'Resistência a Flagelo': 3,
    'Resistência a Muco': 1, 'Resistência a Fome': 3,
    'Velocidade Regeneração': 3, 'Regeneração Veloz': 1,
    'Botânica': 4, 'Geologia': 3, 'Entomologista': 3,
    'Reunir Amigatos': 5, 'Capacidade da Atiradeira': 5,
    'Comer Rapidamente': 3, 'Refeição Grátis': 3,
    'Artilharia Pesada': 2, 'Aumento de Regeneração': 3,
    'Deslizada de Afinidade': 1, 'Clutch Claw Boost': 1,
    'Conversão de Elemento': 1, 'Espancador': 1,
    'Elemento Crítico': 1, 'Elemento Crítico Real': 1,
    'Status Crítico': 1, 'Status Crítico Real': 1,
    'Toque de Mestre': 1, 'Polimento Protetor': 1,
    'Adrenalina': 1, 'Bravura': 1, 'Punição Imediata': 1,
    'Super-regeneração': 1, 'Anular Pressão do Vento': 1,
    'Aumento de Bloqueio': 1, 'Despertar de Dragoveio': 1,
    'Despertar de Dragoveio Real': 1, 'Mais Limite de Vigor': 1,
    'Olhos da Mente/Balística': 1, 'Boa Sorte': 1, 'Sorte Grande': 1,
    'Elemento Gradual': 1, 'Elemento Gradual Real': 1,
    'Fio Nav./Tiro Extra': 1, 'Fio Nav./Tiro Extra Real': 1,
    'Reforço de Capacidade': 1, 'Toda Resistência Elemental': 1,
};

// ============================================================
// Initial State
// ============================================================

const initialBuildState: BuildState = {
    weapon: null,
    armor: { head: null, chest: null, arms: null, waist: null, legs: null },
    charm: null,
    decorations: {
        weapon: [],
        head: [],
        chest: [],
        arms: [],
        waist: [],
        legs: [],
    },
    weaponAugments: [],
    safiAwakenings: [null, null, null, null, null],
    customUpgrades: [],
};

// ============================================================
// Actions
// ============================================================

type BuildAction =
    | { type: 'SET_WEAPON'; payload: WeaponSlot | null }
    | { type: 'SET_ARMOR'; payload: { slot: ArmorType; piece: ArmorSlot | null } }
    | { type: 'SET_CHARM'; payload: CharmSlot | null }
    | { type: 'ADD_DECORATION'; payload: { slot: keyof BuildState['decorations']; index: number; decoration: DecorationSlot } }
    | { type: 'REMOVE_DECORATION'; payload: { slot: keyof BuildState['decorations']; index: number } }
    | { type: 'SET_AUGMENTS'; payload: Augment[] }
    | { type: 'SET_SAFI_AWAKENING'; payload: { index: number; awakening: SafiAwakening | null } }
    | { type: 'SET_CUSTOM_UPGRADES'; payload: CustomUpgrade[] }
    | { type: 'RESET_BUILD' }
    | { type: 'LOAD_BUILD'; payload: BuildState };

// ============================================================
// Reducer
// ============================================================

function buildReducer(state: BuildState, action: BuildAction): BuildState {
    switch (action.type) {
        case 'SET_WEAPON': {
            // Reset weapon-related slots when weapon changes
            const weaponSlots = action.payload?.slots || [];
            return {
                ...state,
                weapon: action.payload,
                decorations: {
                    ...state.decorations,
                    weapon: weaponSlots.map(() => null),
                },
                weaponAugments: [],
                safiAwakenings: [null, null, null, null, null],
                customUpgrades: [],
            };
        }

        case 'SET_ARMOR': {
            const { slot, piece } = action.payload;
            const armorSlots = piece?.slots || [];
            return {
                ...state,
                armor: { ...state.armor, [slot]: piece },
                decorations: {
                    ...state.decorations,
                    [slot]: armorSlots.map(() => null),
                },
            };
        }

        case 'SET_CHARM':
            return { ...state, charm: action.payload };

        case 'ADD_DECORATION': {
            const { slot, index, decoration } = action.payload;
            const updatedSlots = [...state.decorations[slot]];
            updatedSlots[index] = decoration;
            return {
                ...state,
                decorations: { ...state.decorations, [slot]: updatedSlots },
            };
        }

        case 'REMOVE_DECORATION': {
            const { slot, index } = action.payload;
            const updatedSlots = [...state.decorations[slot]];
            updatedSlots[index] = null;
            return {
                ...state,
                decorations: { ...state.decorations, [slot]: updatedSlots },
            };
        }

        case 'SET_AUGMENTS':
            return { ...state, weaponAugments: action.payload };

        case 'SET_SAFI_AWAKENING': {
            const awakenings = [...state.safiAwakenings];
            awakenings[action.payload.index] = action.payload.awakening;
            return { ...state, safiAwakenings: awakenings };
        }

        case 'SET_CUSTOM_UPGRADES':
            return { ...state, customUpgrades: action.payload };

        case 'RESET_BUILD':
            return { ...initialBuildState };

        case 'LOAD_BUILD':
            return { ...action.payload };

        default:
            return state;
    }
}
// ============================================================
// Set Bonus Computation
// ============================================================

function computeSetBonuses(state: BuildState): SetBonus[] {
    // Count armor pieces per SET BONUS (not per armorset variant)
    const bonusCounts = new Map<string, { count: number; tiers: { required: number; skill: string }[] }>();

    for (const piece of Object.values(state.armor)) {
        if (piece?.setBonusName) {
            const existing = bonusCounts.get(piece.setBonusName) || { count: 0, tiers: [] };
            existing.count += 1;
            // Store tiers from the first piece that has them
            if (existing.tiers.length === 0 && piece.setBonusTiers && piece.setBonusTiers.length > 0) {
                existing.tiers = piece.setBonusTiers;
            }
            bonusCounts.set(piece.setBonusName, existing);
        }
    }

    // Safi Essences add +1 to their respective set counts
    state.safiAwakenings.forEach(awk => {
        if (awk?.category === 'set_bonus' && awk.setBonusSet) {
            const existing = bonusCounts.get(awk.setBonusSet) || { count: 0, tiers: [] };
            existing.count += 1;
            bonusCounts.set(awk.setBonusSet, existing);
        }
    });

    const bonuses: SetBonus[] = [];
    for (const [setName, data] of bonusCounts) {
        bonuses.push({
            setName,
            piecesEquipped: data.count,
            tiers: data.tiers.map(t => ({
                piecesRequired: t.required,
                bonus: t.skill,
                active: data.count >= t.required,
            })),
        });
    }

    return bonuses;
}

// ============================================================
// Computed Stats
// ============================================================

function computeSkills(state: BuildState): SkillLevel[] {
    const skillMap = new Map<string, { level: number; sources: string[] }>();

    const addSkill = (skill: SkillRef, source: string) => {
        const existing = skillMap.get(skill.name) || { level: 0, sources: [] };
        existing.level += skill.level;
        existing.sources.push(source);
        skillMap.set(skill.name, existing);
    };

    // Armor skills
    for (const [, piece] of Object.entries(state.armor)) {
        if (piece) {
            piece.skills.forEach(s => addSkill(s, piece.name));
        }
    }

    // Charm skills
    if (state.charm) {
        state.charm.skills.forEach(s => addSkill(s, state.charm!.name));
    }

    // Decoration skills
    for (const [slotName, decos] of Object.entries(state.decorations)) {
        decos.forEach(d => {
            if (d) {
                // Handle combo jewels (tier 4) which have multiple skills
                if (d.skills && d.skills.length > 0) {
                    d.skills.forEach(s => addSkill(s, `${d.name} (${slotName})`));
                } else if (d.skill) {
                    // Fallback for single skill jewels
                    addSkill(d.skill, `${d.name} (${slotName})`);
                }
            }
        });
    }

    // Weapon innate skills (Kjarr etc.)
    if (state.weapon?.innateSkills) {
        state.weapon.innateSkills.forEach(s => addSkill(s, state.weapon!.name));
    }

    // 6.6: Kjarr weapons have Critical Element built-in
    if (state.weapon?.isKjarr || state.weapon?.name?.toLowerCase().includes('kjarr')) {
        if (!skillMap.has('Critical Element')) {
            addSkill({ name: 'Critical Element', level: 1 }, `${state.weapon.name} (Kjarr)`);
        }
    }

    // Safi awakening skills
    state.safiAwakenings.forEach(a => {
        if (a?.skillRef) addSkill(a.skillRef, `Safi: ${a.name}`);
    });

    // 8.4: Determine active skill secrets for dynamic caps
    const setBonuses = computeSetBonuses(state);

    // Find which secrets are active
    const activeSecretSkills = new Set<string>();

    for (const bonus of setBonuses) {
        const secretEntries = SKILL_SECRETS[bonus.setName];
        if (!secretEntries) continue;

        for (const entry of secretEntries) {
            if (bonus.piecesEquipped >= entry.pieces) {
                if (entry.unlockedSkills.includes('ALL')) {
                    activeSecretSkills.add('ALL');
                } else {
                    entry.unlockedSkills.forEach((s: string) => activeSecretSkills.add(s));
                }
            }
        }
    }

    const isAllSecretsActive = activeSecretSkills.has('ALL');

    return Array.from(skillMap.entries()).map(([name, data]) => {
        const maxLevel = SKILL_MAX_LEVELS[name] || 0;
        const secretMax = SKILL_SECRET_MAX_LEVELS[name] || 0;
        const isSecretActive = isAllSecretsActive || activeSecretSkills.has(name);

        return {
            name,
            currentLevel: data.level,
            maxLevel,
            secretMaxLevel: secretMax,
            isSecretActive,
            sources: data.sources,
        };
    }).sort((a, b) => b.currentLevel - a.currentLevel);
}

function computeBasicStats(state: BuildState): ComputedStats {
    const activeSkills = computeSkills(state);
    const activeSetBonuses = computeSetBonuses(state);

    const skillRefs: SkillRef[] = activeSkills.map(s => ({ name: s.name, level: s.currentLevel }));

    const weapon = state.weapon;
    const weaponAttack = weapon?.attack || 0;
    const weaponAttackTrue = weapon?.attackTrue;
    const weaponType = weapon?.type || 'great-sword';
    const weaponAffinity = weapon?.affinity || 0;

    // --- Breakdown Calculation ---
    const weaponAffinityBase = weaponAffinity;
    let skillAffinityStatic = 0;
    let skillAffinityConditional = 0;

    const CONDITIONAL_SKILLS = ['Weakness Exploit', 'Agitator', 'Maximum Might', 'Latent Power',
        'Exploração de Fraqueza', 'Agitador', 'Poder Máximo', 'Poder Latente'];

    for (const skill of skillRefs) {
        const bonuses = SKILL_BONUSES[skill.name];
        if (!bonuses) continue;
        const bonus = bonuses[Math.min(skill.level, bonuses.length - 1)] || {};
        if (bonus.affinity) {
            if (CONDITIONAL_SKILLS.includes(skill.name)) {
                skillAffinityConditional += bonus.affinity;
            } else {
                skillAffinityStatic += bonus.affinity;
            }
        }
    }

    // Add affinity from Augments/Safi/Custom
    let extraAffinity = calculateAffinity(0, [], state.weaponAugments, state.safiAwakenings, state.customUpgrades);
    skillAffinityStatic += extraAffinity;

    const baseTrueRaw = weaponAttackTrue || (weaponAttack / (WEAPON_MULTIPLIERS[weaponType] || 1));
    let skillRawStatic = 0;
    let skillRawConditional = 0;
    let multiplierStatic = 1.0;

    const CONDITIONAL_RAW_SKILLS = ['Agitator', 'Peak Performance', 'Resentment', 'Coalescence', 'Offensive Guard',
        'Agitador', 'Desempenho Máximo', 'Indignação', 'Coalescência', 'Bloqueio Ofensivo'];

    for (const skill of skillRefs) {
        const bonuses = SKILL_BONUSES[skill.name];
        if (!bonuses) continue;
        const bonus = bonuses[Math.min(skill.level, bonuses.length - 1)] || {};
        if (bonus.raw) {
            if (CONDITIONAL_RAW_SKILLS.includes(skill.name)) {
                skillRawConditional += bonus.raw;
            } else {
                skillRawStatic += bonus.raw;
            }
        }
        if (bonus.rawMult) {
            multiplierStatic *= bonus.rawMult;
        }
    }

    // Add extra raw from Augments/Safi/Custom
    // We can use calculateTrueRaw(0, 0, ...) to get just the extras
    let extraRaw = calculateTrueRaw(0, 0, weaponType, [], state.weaponAugments, state.safiAwakenings, state.customUpgrades);
    skillRawStatic += extraRaw;

    // --- Final Values ---
    const trueRaw = weapon
        ? calculateTrueRaw(weaponAttack, weaponAttackTrue, weaponType, skillRefs, state.weaponAugments, state.safiAwakenings, state.customUpgrades)
        : 0;

    const affinity = weapon
        ? calculateAffinity(weaponAffinity, skillRefs, state.weaponAugments, state.safiAwakenings, state.customUpgrades)
        : 0;

    const sharpnessColor = weapon?.sharpnessColor || 'white';

    const critBoostSkill = activeSkills.find(s => s.name === 'Critical Boost' || s.name === 'Reforço Crítico');
    const critBoostLevel = critBoostSkill?.currentLevel || 0;

    const efr = weapon
        ? calculateEFR(trueRaw, sharpnessColor, affinity, critBoostLevel)
        : 0;

    const elementDamage = (weapon?.element && weapon.element.damage)
        ? calculateElementalEFR(weapon.element.damage, sharpnessColor, skillRefs, weapon.element.type)
        : 0;

    // Defense
    let totalDefense = weapon?.defense || 0;
    for (const piece of Object.values(state.armor)) {
        if (piece) totalDefense += (typeof piece.defense === 'number' ? piece.defense : piece.defense?.base || 0);
    }

    const bloat = WEAPON_MULTIPLIERS[weaponType] || 1;
    const displayAttack = Math.round(trueRaw * bloat);

    // Collect active secret names
    const skillSecretNames: string[] = [];
    for (const bonus of activeSetBonuses) {
        if (SKILL_SECRETS[bonus.setName]) {
            const entries = SKILL_SECRETS[bonus.setName];
            for (const entry of entries) {
                if (bonus.piecesEquipped >= entry.pieces && entry.unlockedSkills.length > 0) {
                    skillSecretNames.push(bonus.setName);
                }
            }
        }
    }

    return {
        trueRaw: Math.round(trueRaw * 10) / 10,
        displayAttack,
        affinity,
        effectiveAffinity: Math.max(-100, Math.min(100, affinity)),
        affinityBreakdown: {
            base: weaponAffinityBase,
            skills: skillAffinityStatic,
            conditional: skillAffinityConditional
        },
        attackBreakdown: {
            base: Math.round(baseTrueRaw * 10) / 10,
            skills: Math.round(skillRawStatic * 10) / 10,
            conditional: Math.round(skillRawConditional * multiplierStatic * 10) / 10
        },
        efr: Math.round(efr * 10) / 10,
        elementDamage: Math.round(elementDamage * 10) / 10,
        defense: totalDefense,
        activeSkills,
        activeSetBonuses,
        skillSecrets: skillSecretNames,
        sharpnessColor,
    };
}

// ============================================================
// Context
// ============================================================

interface BuildContextType {
    buildState: BuildState;
    computedStats: ComputedStats;
    dispatch: React.Dispatch<BuildAction>;
}

const BuildContext = createContext<BuildContextType | undefined>(undefined);

export const useBuildContext = () => {
    const context = useContext(BuildContext);
    if (!context) {
        throw new Error('useBuildContext must be used within a BuildProvider');
    }
    return context;
};

interface BuildProviderProps {
    children: ReactNode;
}

export const BuildProvider: React.FC<BuildProviderProps> = ({ children }) => {
    const [buildState, dispatch] = useReducer(buildReducer, initialBuildState);

    const computedStats = useMemo(() => computeBasicStats(buildState), [buildState]);

    return (
        <BuildContext.Provider value={{ buildState, computedStats, dispatch }}>
            {children}
        </BuildContext.Provider>
    );
};
