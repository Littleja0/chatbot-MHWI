/**
 * Offensive Skill Bonuses — maps skill name → per-level bonuses.
 *
 * Each entry: { raw: flat attack, rawMult: % mult, affinity: %, element: flat, elementMult: % }
 * Source: MHW:I community datasheets
 */

export interface SkillBonusEntry {
    raw?: number;          // flat raw bonus
    rawMult?: number;      // multiplicative raw bonus (e.g. 1.05 = 5%)
    affinity?: number;     // flat affinity %
    element?: number;      // flat element bonus
    elementMult?: number;  // multiplicative element bonus
    critDamage?: number;   // critical damage multiplier override
}

export const SKILL_BONUSES: Record<string, SkillBonusEntry[]> = {
    // --- Attack Boost ---
    'Attack Boost': [
    /* Lv0 */ {},
    /* Lv1 */ { raw: 3 },
    /* Lv2 */ { raw: 6 },
    /* Lv3 */ { raw: 9 },
    /* Lv4 */ { raw: 12, affinity: 5 },    // 7 base + 5% affinity
    /* Lv5 */ { raw: 15, affinity: 5 },
    /* Lv6 */ { raw: 18, affinity: 5 },
    /* Lv7 */ { raw: 21, affinity: 5 },
    ],

    // --- Critical Eye ---
    'Critical Eye': [
        {},
        { affinity: 5 },
        { affinity: 10 },
        { affinity: 15 },
        { affinity: 20 },
        { affinity: 25 },
        { affinity: 30 },
        { affinity: 40 },
    ],

    // --- Weakness Exploit ---
    'Weakness Exploit': [
        {},
        { affinity: 15 },   // on weak spots
        { affinity: 30 },   // on weak spots
        { affinity: 50 },   // 30% weak + 20% tenderized
    ],

    // --- Critical Boost ---
    'Critical Boost': [
        {},
        { critDamage: 1.30 },
        { critDamage: 1.35 },
        { critDamage: 1.40 },
    ],

    // --- Agitator ---
    'Agitator': [
        {},
        { raw: 4, affinity: 5 },
        { raw: 8, affinity: 5 },
        { raw: 12, affinity: 7 },
        { raw: 16, affinity: 7 },
        { raw: 20, affinity: 10 },
        { raw: 24, affinity: 15 },
        { raw: 28, affinity: 20 },
    ],

    // --- Peak Performance ---
    'Peak Performance': [
        {},
        { raw: 5 },
        { raw: 10 },
        { raw: 20 },
    ],

    // --- Resentment ---
    'Resentment': [
        {},
        { raw: 5 },
        { raw: 10 },
        { raw: 15 },
        { raw: 20 },
        { raw: 25 },
    ],

    // --- Coalescence ---
    'Coalescence': [
        {},
        { raw: 12, element: 30 },
        { raw: 15, element: 60 },
        { raw: 18, element: 90 },
    ],

    // --- Heroics ---
    'Heroics': [
        {},
        { raw: 0 },   // defense only
        { raw: 0 },
        { raw: 0 },
        { raw: 0 },
        { rawMult: 1.25 },
        { raw: 0 },
        { rawMult: 1.40 },
    ],

    // --- Fortify ---
    'Fortify': [
        {},
        { rawMult: 1.10 },  // 10% per cart, stackable
    ],

    // --- Non-elemental Boost (Elementless) ---
    'Non-elemental Boost': [
        {},
        { rawMult: 1.05 },
    ],

    // --- Offensive Guard ---
    'Offensive Guard': [
        {},
        { rawMult: 1.05 },
        { rawMult: 1.10 },
        { rawMult: 1.15 },
    ],

    // --- Maximum Might ---
    'Maximum Might': [
        {},
        { affinity: 10 },
        { affinity: 20 },
        { affinity: 30 },
        { affinity: 40 },
        { affinity: 40 },  // secret
    ],

    // --- Latent Power ---
    'Latent Power': [
        {},
        { affinity: 10 },
        { affinity: 20 },
        { affinity: 30 },
        { affinity: 40 },
        { affinity: 50 },
        { affinity: 50 },
        { affinity: 60 },
    ],

    // --- Element skills ---
    'Fire Attack': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
    'Water Attack': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
    'Thunder Attack': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
    'Ice Attack': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
    'Dragon Attack': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
};
