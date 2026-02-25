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
    | { type: 'RESET_BUILD' };

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

        default:
            return state;
    }
}
// ============================================================
// Set Bonus Computation
// ============================================================

function computeSetBonuses(state: BuildState): SetBonus[] {
    // Count armor pieces per set
    const setCounts = new Map<string, number>();
    for (const piece of Object.values(state.armor)) {
        if (piece?.setName) {
            setCounts.set(piece.setName, (setCounts.get(piece.setName) || 0) + 1);
        }
    }

    // Safi Essences add +1 to their respective set counts
    state.safiAwakenings.forEach(awk => {
        if (awk?.category === 'set_bonus' && awk.setBonusSet) {
            setCounts.set(awk.setBonusSet, (setCounts.get(awk.setBonusSet) || 0) + 1);
        }
    });

    const bonuses: SetBonus[] = [];
    for (const [setName, count] of setCounts) {
        bonuses.push({
            setName,
            piecesEquipped: count,
            tiers: [],
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
            if (d) addSkill(d.skill, `${d.name} (${slotName})`);
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
        const secretMax = SKILL_SECRET_MAX_LEVELS[name] || 0;
        const isSecretActive = isAllSecretsActive || activeSecretSkills.has(name);

        return {
            name,
            currentLevel: data.level,
            maxLevel: 0,
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

    const trueRaw = weapon
        ? calculateTrueRaw(weaponAttack, weaponAttackTrue, weaponType, skillRefs, state.weaponAugments, state.safiAwakenings, state.customUpgrades)
        : 0;

    const affinity = weapon
        ? calculateAffinity(weaponAffinity, skillRefs, state.weaponAugments, state.safiAwakenings, state.customUpgrades)
        : 0;

    const sharpnessColor = weapon?.sharpnessColor || 'white';

    const critBoostSkill = activeSkills.find(s => s.name === 'Critical Boost');
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
