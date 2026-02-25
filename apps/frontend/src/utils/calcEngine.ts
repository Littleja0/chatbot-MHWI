/**
 * calcEngine.ts — EFR (Effective Raw) calculation engine.
 *
 * Pure functions for damage calculation. No side effects, no state.
 * Designed to be used with useMemo() in BuildContext.
 */

import { SharpnessColor, SkillRef, Augment, SafiAwakening, CustomUpgrade } from '../types/builder';
import { WEAPON_MULTIPLIERS } from '../data/weaponMultipliers';
import { SHARPNESS_RAW_MULTIPLIERS, SHARPNESS_ELEMENT_MULTIPLIERS } from '../data/sharpnessMultipliers';
import { SKILL_BONUSES, SkillBonusEntry } from '../data/skillBonuses';

// ============================================================
// Helpers
// ============================================================

function getSkillBonus(skillName: string, level: number): SkillBonusEntry {
    const bonuses = SKILL_BONUSES[skillName];
    if (!bonuses) return {};
    return bonuses[Math.min(level, bonuses.length - 1)] || {};
}

function clamp(value: number, min: number, max: number): number {
    return Math.max(min, Math.min(max, value));
}

// ============================================================
// True Raw Calculation
// ============================================================

/**
 * Calculate True Raw from weapon stats + all modifiers.
 *
 * True Raw = (Display Attack / Bloat Value) + Flat Bonuses + Augment Bonuses + Safi/Kulve Bonuses
 * Then apply multiplicative bonuses.
 */
export function calculateTrueRaw(
    weaponAttack: number,
    weaponAttackTrue: number | undefined,
    weaponType: string,
    activeSkills: SkillRef[],
    augments: Augment[],
    safiAwakenings: (SafiAwakening | null)[],
    customUpgrades: CustomUpgrade[],
): number {
    // Start with true raw (if available from DB) or calculate from display attack
    let trueRaw = weaponAttackTrue || weaponAttack;
    if (!weaponAttackTrue && WEAPON_MULTIPLIERS[weaponType]) {
        trueRaw = weaponAttack / WEAPON_MULTIPLIERS[weaponType];
    }

    // Flat bonuses from skills
    let flatBonus = 0;
    let multBonus = 1.0;

    for (const skill of activeSkills) {
        const bonus = getSkillBonus(skill.name, skill.level);
        if (bonus.raw) flatBonus += bonus.raw;
        if (bonus.rawMult) multBonus *= bonus.rawMult;
    }

    // Augment bonuses
    for (const aug of augments) {
        if (aug.effect === 'attack') {
            flatBonus += aug.value;
        }
    }

    // Safi awakening bonuses
    for (const awakening of safiAwakenings) {
        if (awakening && awakening.category === 'attack') {
            flatBonus += awakening.value;
        }
    }

    // Custom upgrade bonuses (Kulve)
    for (const upgrade of customUpgrades) {
        if (upgrade.stat === 'attack') {
            flatBonus += upgrade.value;
        }
    }

    return (trueRaw + flatBonus) * multBonus;
}


// ============================================================
// Affinity Calculation
// ============================================================

/**
 * Calculate effective affinity from weapon base + all modifiers.
 */
export function calculateAffinity(
    weaponAffinity: number,
    activeSkills: SkillRef[],
    augments: Augment[],
    safiAwakenings: (SafiAwakening | null)[],
    customUpgrades: CustomUpgrade[],
): number {
    let affinity = weaponAffinity;

    // Skill bonuses
    for (const skill of activeSkills) {
        const bonus = getSkillBonus(skill.name, skill.level);
        if (bonus.affinity) affinity += bonus.affinity;
    }

    // Augment bonuses
    for (const aug of augments) {
        if (aug.effect === 'affinity') {
            affinity += aug.value;
        }
    }

    // Safi awakening bonuses
    for (const awakening of safiAwakenings) {
        if (awakening && awakening.category === 'affinity') {
            affinity += awakening.value;
        }
    }

    // Custom upgrade bonuses
    for (const upgrade of customUpgrades) {
        if (upgrade.stat === 'affinity') {
            affinity += upgrade.value;
        }
    }

    return clamp(affinity, -100, 100);
}


// ============================================================
// EFR (Effective Raw) Calculation
// ============================================================

/**
 * EFR = True Raw × Sharpness Multiplier × (1 + (Affinity/100 × (Crit Multiplier - 1)))
 */
export function calculateEFR(
    trueRaw: number,
    sharpnessColor: SharpnessColor,
    affinity: number,
    critBoostLevel: number = 0,
): number {
    const sharpMult = SHARPNESS_RAW_MULTIPLIERS[sharpnessColor] || 1.0;

    // Critical damage multiplier: base 1.25, modified by Critical Boost
    let critMult = 1.25;
    const critBoostBonus = getSkillBonus('Critical Boost', critBoostLevel);
    if (critBoostBonus.critDamage) {
        critMult = critBoostBonus.critDamage;
    }

    // Negative affinity uses 0.75 multiplier (Feeble Hit)
    let critFactor: number;
    if (affinity >= 0) {
        critFactor = 1 + (affinity / 100) * (critMult - 1);
    } else {
        critFactor = 1 + (affinity / 100) * (1 - 0.75);  // Feeble hit reduces to 75%
    }

    return trueRaw * sharpMult * critFactor;
}


// ============================================================
// Elemental EFR
// ============================================================

/**
 * Calculate effective elemental damage.
 *
 * Effective Element = (Base Element + Flat Bonuses) × Element Mult × Sharpness Elemental Mult
 */
export function calculateElementalEFR(
    elementBase: number,
    sharpnessColor: SharpnessColor,
    activeSkills: SkillRef[],
    elementType?: string,
): number {
    if (!elementBase || elementBase <= 0) return 0;

    // True element (display / 10 in MHW, but DB may already be true)
    let element = elementBase;

    // Find matching element skill
    const elementSkillMap: Record<string, string> = {
        'fire': 'Fire Attack',
        'water': 'Water Attack',
        'thunder': 'Thunder Attack',
        'ice': 'Ice Attack',
        'dragon': 'Dragon Attack',
    };

    const skillName = elementType ? elementSkillMap[elementType.toLowerCase()] : null;
    let flatBonus = 0;
    let multBonus = 1.0;

    if (skillName) {
        for (const skill of activeSkills) {
            if (skill.name === skillName) {
                const bonus = getSkillBonus(skillName, skill.level);
                if (bonus.element) flatBonus += bonus.element;
                if (bonus.elementMult) multBonus *= bonus.elementMult;
                break;
            }
        }
    }

    // Coalescence and other global element bonuses
    for (const skill of activeSkills) {
        if (skill.name !== skillName) {
            const bonus = getSkillBonus(skill.name, skill.level);
            if (bonus.element) flatBonus += bonus.element;
        }
    }

    const sharpMult = SHARPNESS_ELEMENT_MULTIPLIERS[sharpnessColor] || 1.0;

    return (element + flatBonus) * multBonus * sharpMult;
}
