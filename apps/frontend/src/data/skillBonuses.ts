/**
 * Offensive Skill Bonuses — maps skill name → per-level bonuses.
 *
 * Each entry: { raw: flat attack, rawMult: % mult, affinity: %, element: flat, elementMult: % }
 * Source: MHW:I community datasheets
 * 
 * NOTE: Keys use **Portuguese** names to match DB output.
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
    // --- Attack Boost / Reforço de Ataque ---
    'Reforço de Ataque': [
    /* Lv0 */ {},
    /* Lv1 */ { raw: 3 },
    /* Lv2 */ { raw: 6 },
    /* Lv3 */ { raw: 9 },
    /* Lv4 */ { raw: 12, affinity: 5 },
    /* Lv5 */ { raw: 15, affinity: 5 },
    /* Lv6 */ { raw: 18, affinity: 5 },
    /* Lv7 */ { raw: 21, affinity: 5 },
    ],
    'Attack Boost': [
        {},
        { raw: 3 },
        { raw: 6 },
        { raw: 9 },
        { raw: 12, affinity: 5 },
        { raw: 15, affinity: 5 },
        { raw: 18, affinity: 5 },
        { raw: 21, affinity: 5 },
    ],

    // --- Critical Eye / Olho Crítico ---
    'Olho Crítico': [
        {},
        { affinity: 5 },
        { affinity: 10 },
        { affinity: 15 },
        { affinity: 20 },
        { affinity: 25 },
        { affinity: 30 },
        { affinity: 40 },
    ],
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

    // --- Weakness Exploit / Exploração de Fraqueza ---
    'Exploração de Fraqueza': [
        {},
        { affinity: 15 },
        { affinity: 30 },
        { affinity: 50 },
    ],
    'Weakness Exploit': [
        {},
        { affinity: 15 },
        { affinity: 30 },
        { affinity: 50 },
    ],

    // --- Critical Boost / Reforço Crítico ---
    'Reforço Crítico': [
        {},
        { critDamage: 1.30 },
        { critDamage: 1.35 },
        { critDamage: 1.40 },
    ],
    'Critical Boost': [
        {},
        { critDamage: 1.30 },
        { critDamage: 1.35 },
        { critDamage: 1.40 },
    ],

    // --- Agitator / Agitador ---
    'Agitador': [
        {},
        { raw: 4, affinity: 5 },
        { raw: 8, affinity: 5 },
        { raw: 12, affinity: 7 },
        { raw: 16, affinity: 7 },
        { raw: 20, affinity: 10 },
        { raw: 24, affinity: 15 },
        { raw: 28, affinity: 20 },
    ],
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

    // --- Peak Performance / Desempenho Máximo ---
    'Desempenho Máximo': [
        {},
        { raw: 5 },
        { raw: 10 },
        { raw: 20 },
    ],
    'Peak Performance': [
        {},
        { raw: 5 },
        { raw: 10 },
        { raw: 20 },
    ],

    // --- Resentment / Indignação ---
    'Indignação': [
        {},
        { raw: 5 },
        { raw: 10 },
        { raw: 15 },
        { raw: 20 },
        { raw: 25 },
    ],
    'Resentment': [
        {},
        { raw: 5 },
        { raw: 10 },
        { raw: 15 },
        { raw: 20 },
        { raw: 25 },
    ],

    // --- Coalescence / Coalescência ---
    'Coalescência': [
        {},
        { raw: 12, element: 30 },
        { raw: 15, element: 60 },
        { raw: 18, element: 90 },
    ],
    'Coalescence': [
        {},
        { raw: 12, element: 30 },
        { raw: 15, element: 60 },
        { raw: 18, element: 90 },
    ],

    // --- Heroics / Heroísmo ---
    'Heroísmo': [
        {},
        { raw: 0 },
        { raw: 0 },
        { raw: 0 },
        { raw: 0 },
        { rawMult: 1.25 },
        { raw: 0 },
        { rawMult: 1.40 },
    ],
    'Heroics': [
        {},
        { raw: 0 },
        { raw: 0 },
        { raw: 0 },
        { raw: 0 },
        { rawMult: 1.25 },
        { raw: 0 },
        { rawMult: 1.40 },
    ],

    // --- Fortify / Fortificar ---
    'Fortificar': [
        {},
        { rawMult: 1.10 },
    ],
    'Fortify': [
        {},
        { rawMult: 1.10 },
    ],

    // --- Non-elemental Boost / Reforço Não Elemental ---
    'Reforço Não Elemental': [
        {},
        { rawMult: 1.05 },
    ],
    'Non-elemental Boost': [
        {},
        { rawMult: 1.05 },
    ],

    // --- Offensive Guard / Bloqueio Ofensivo ---
    'Bloqueio Ofensivo': [
        {},
        { rawMult: 1.05 },
        { rawMult: 1.10 },
        { rawMult: 1.15 },
    ],
    'Offensive Guard': [
        {},
        { rawMult: 1.05 },
        { rawMult: 1.10 },
        { rawMult: 1.15 },
    ],

    // --- Maximum Might / Poder Máximo ---
    'Poder Máximo': [
        {},
        { affinity: 10 },
        { affinity: 20 },
        { affinity: 30 },
        { affinity: 40 },
        { affinity: 40 },
    ],
    'Maximum Might': [
        {},
        { affinity: 10 },
        { affinity: 20 },
        { affinity: 30 },
        { affinity: 40 },
        { affinity: 40 },
    ],

    // --- Latent Power / Poder Latente ---
    'Poder Latente': [
        {},
        { affinity: 10 },
        { affinity: 20 },
        { affinity: 30 },
        { affinity: 40 },
        { affinity: 50 },
        { affinity: 50 },
        { affinity: 60 },
    ],
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
    'Ataque de Fogo': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
    'Fire Attack': [
        {},
        { element: 30 },
        { element: 60 },
        { element: 100 },
        { element: 100, elementMult: 1.05 },
        { element: 100, elementMult: 1.10 },
        { element: 100, elementMult: 1.20 },
    ],
    'Ataque de Água': [
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
    'Ataque de Raio': [
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
    'Ataque de Gelo': [
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
    'Ataque de Dragão': [
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
