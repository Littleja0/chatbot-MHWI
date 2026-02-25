/**
 * Skill Secrets — Set bonuses that unlock higher skill caps.
 *
 * When N pieces of the set are equipped, the listed skills can exceed
 * their normal max level up to the secret max.
 *
 * Source: MHW:I Iceborne Master Rank set bonuses
 */

export interface SkillSecretEntry {
    pieces: number;
    unlockedSkills: string[];  // skill names that get unlocked, or "ALL" for Fatalis
}

export const SKILL_SECRETS: Record<string, SkillSecretEntry[]> = {
    // --- Raging Brachydios (Agitator Secret) ---
    'Raging Brachydios Mastery': [
        { pieces: 2, unlockedSkills: ['Agitator'] },
    ],

    // --- Gold Rathian (Divine Blessing Secret) ---
    'True Critical Status': [
        { pieces: 2, unlockedSkills: ['Divine Blessing'] },
    ],

    // --- Silver Rathalos (Slinger Capacity Secret / True Critical Element) ---
    'True Critical Element': [
        { pieces: 4, unlockedSkills: ['Critical Eye'] },
    ],

    // --- Ruiner Nergigante (Hasten Recovery) ---
    'Ruiner Nergigante Hunger': [
        { pieces: 3, unlockedSkills: ['Stamina Surge'] },
    ],

    // --- Zorah Magdaros MR (Artillery Secret) ---
    'Zorah Magdaros Mastery': [
        { pieces: 3, unlockedSkills: ['Artillery'] },
    ],

    // --- Stygian Zinogre (Latent Power Secret) ---
    'Stygian Zinogre Mastery': [
        { pieces: 3, unlockedSkills: ['Latent Power'] },
    ],

    // --- Safi'jiiva (Dragonvein Awakening) ---
    "Safi'jiiva Seal": [
        { pieces: 3, unlockedSkills: ['Resentment'] },
    ],

    // --- Furious Rajang (Maximum Might Secret) ---
    'Furious Rajang Mastery': [
        { pieces: 2, unlockedSkills: ['Maximum Might'] },
    ],

    // --- Fatalis (Transcendence) —  unlocks ALL skill caps ---
    'Fatalis Mastery': [
        { pieces: 2, unlockedSkills: ['ALL'] },
    ],

    // --- Teostra (Master's Touch) — not a secret but useful for tracking ---
    "Teostra Technique": [
        { pieces: 3, unlockedSkills: [] },  // Master's Touch is a separate bonus, not a skill cap unlock
    ],

    // --- Velkhana (Frostcraft) ---
    'Velkhana Divinity': [
        { pieces: 2, unlockedSkills: [] },
    ],

    // --- Buff Body (Mushroomancer secret) ---
    'Buff Body': [
        { pieces: 2, unlockedSkills: ['Mushroomancer'] },
    ],
};

/**
 * Extended skill max levels when their secret is unlocked.
 * Normal max is from the database; this provides the extended max.
 */
export const SKILL_SECRET_MAX_LEVELS: Record<string, number> = {
    'Agitator': 7,
    'Divine Blessing': 5,
    'Artillery': 5,
    'Latent Power': 7,
    'Maximum Might': 5,
    'Resentment': 5,
    'Heroics': 7,
    'Mushroomancer': 3,
    'Fortify': 1,
};
