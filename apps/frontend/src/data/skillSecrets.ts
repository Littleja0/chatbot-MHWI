/**
 * Skill Secrets — Set bonuses that unlock higher skill caps.
 *
 * When N pieces of the set are equipped, the listed skills can exceed
 * their normal max level up to the secret max.
 *
 * NOTE: Keys use **Portuguese** set bonus names to match DB output.
 * Unlocked skill names also in PT.
 *
 * Source: MHW:I Iceborne Master Rank set bonuses
 */

export interface SkillSecretEntry {
    pieces: number;
    unlockedSkills: string[];  // skill names that get unlocked, or "ALL" for Fatalis
}

export const SKILL_SECRETS: Record<string, SkillSecretEntry[]> = {
    // --- Raging Brachydios (Agitator Secret) ---
    'Vontade de Brachydios': [
        { pieces: 2, unlockedSkills: ['Agitador'] },
    ],

    // --- Gold Rathian (Divine Blessing Secret) ---
    'Alma de Rath': [
        { pieces: 2, unlockedSkills: ['Bênção Divina'] },
        { pieces: 4, unlockedSkills: ['Bênção Divina'] },
    ],

    // --- Silver Rathalos (True Critical Element) ---
    'Alma de Rathalos Prateada': [
        { pieces: 4, unlockedSkills: ['Olho Crítico'] },
    ],

    // --- Furious Rajang (Maximum Might Secret + Heroics Secret) ---
    'Vontade de Rajang': [
        { pieces: 2, unlockedSkills: ['Poder Máximo'] },
        { pieces: 4, unlockedSkills: ['Heroísmo'] },
    ],

    // --- Safi'jiiva (Dragonvein Awakening) ---
    "Selo de Safi'jiiva": [
        { pieces: 3, unlockedSkills: ['Indignação'] },
    ],

    // --- Teostra (Master's Touch) ---
    'Técnica de Teostra': [
        { pieces: 3, unlockedSkills: [] },  // Master's Touch isn't a cap unlock
    ],

    // --- Velkhana (Frostcraft) ---
    'Graça de Velkhana': [
        { pieces: 2, unlockedSkills: [] },
    ],

    // --- Kushala Daora (Nullify Wind Pressure) ---
    'Voo de Kushala Daora': [
        { pieces: 3, unlockedSkills: [] },
    ],

    // --- Nergigante (Hasten Recovery) ---
    'Instinto de Nergigante': [
        { pieces: 3, unlockedSkills: ['Surto de Vigor'] },
    ],

    // --- Blackveil Vaal Hazak ---
    'Vitalidade de Vaal Hazak': [
        { pieces: 3, unlockedSkills: [] },
    ],

    // --- Namielle ---
    'Graça de Namielle': [
        { pieces: 2, unlockedSkills: [] },
        { pieces: 4, unlockedSkills: [] },
    ],

    // --- Zinogre Stygian (Latent Power Secret) ---
    'Vontade do Zinogre Estígio': [
        { pieces: 3, unlockedSkills: ['Poder Latente'] },
    ],

    // --- Fatalis (Transcendence) — unlocks ALL skill caps ---
    'Graça de Fatalis': [
        { pieces: 2, unlockedSkills: ['ALL'] },
    ],

    // English fallback keys
    'Raging Brachydios Mastery': [
        { pieces: 2, unlockedSkills: ['Agitator', 'Agitador'] },
    ],
    'Fatalis Mastery': [
        { pieces: 2, unlockedSkills: ['ALL'] },
    ],
    "Safi'jiiva Seal": [
        { pieces: 3, unlockedSkills: ['Resentment', 'Indignação'] },
    ],
    'Teostra Technique': [
        { pieces: 3, unlockedSkills: [] },
    ],
};

/**
 * Extended skill max levels when their secret is unlocked.
 * Uses PT names to match DB output.
 */
export const SKILL_SECRET_MAX_LEVELS: Record<string, number> = {
    'Agitador': 7,
    'Agitator': 7,
    'Bênção Divina': 5,
    'Divine Blessing': 5,
    'Artilharia': 5,
    'Artillery': 5,
    'Poder Latente': 7,
    'Latent Power': 7,
    'Poder Máximo': 5,
    'Maximum Might': 5,
    'Indignação': 5,
    'Resentment': 5,
    'Heroísmo': 7,
    'Heroics': 7,
    'Cogumelaria': 3,
    'Mushroomancer': 3,
    'Fortificar': 1,
    'Fortify': 1,
};
