// ============================================================
// Builder Types — MHW:I Build Creator
// ============================================================

// --- Equipment Pieces ---

export type ArmorType = 'head' | 'chest' | 'arms' | 'waist' | 'legs';
export type WeaponType =
    | 'great-sword' | 'long-sword' | 'sword-and-shield' | 'dual-blades'
    | 'hammer' | 'hunting-horn' | 'lance' | 'gunlance'
    | 'switch-axe' | 'charge-blade' | 'insect-glaive'
    | 'light-bowgun' | 'heavy-bowgun' | 'bow';

export type SharpnessColor = 'red' | 'orange' | 'yellow' | 'green' | 'blue' | 'white' | 'purple';

export interface SkillRef {
    name: string;
    level: number;
    description?: string;
}

export interface WeaponSlot {
    id: number;
    name: string;
    namePt: string;
    type: WeaponType;
    rarity: number;
    attack: number;
    attackTrue?: number;       // true raw from DB (attack_true)
    affinity: number;
    defense?: number;          // some weapons grant defense bonus
    element?: { type: string; damage: number; hidden?: boolean } | null;
    slots: number[];           // ex: [3, 2, 0] → tier 3, tier 2, empty
    sharpness?: string;        // raw sharpness data from DB
    sharpnessColor?: SharpnessColor;  // computed highest sharpness
    elderseal?: string;
    isSafi?: boolean;
    isKjarr?: boolean;
    isCustomizable?: boolean;  // Taroth weapons
    innateSkills?: SkillRef[]; // ex: Kjarr Critical Element
    armorsetBonusId?: number;  // for Safi weapons
    category?: string;         // weapon category from DB
}

export interface ArmorSlot {
    id: number;
    name: string;
    type: ArmorType;
    rarity: number;
    rank?: string;
    setName?: string;
    setId?: number;            // armorset_id for set bonus tracking
    defense: number | { base: number; max?: number };
    resistances?: {
        fire?: number;
        water?: number;
        thunder?: number;
        ice?: number;
        dragon?: number;
    };
    slots: number[];
    skills: SkillRef[];
    setBonusName?: string | null;
    setBonusTiers?: { required: number; skill: string }[];
}

export interface CharmSlot {
    id: number;
    name: string;
    rarity: number;
    skills: SkillRef[];
}

export interface DecorationSlot {
    id: number;
    name: string;
    tier: number;           // 1-4
    rarity?: number;
    skill: SkillRef;
    skills?: SkillRef[];    // multiple skills (e.g. combo jewels)
}

// --- Weapon Customization ---

export interface Augment {
    id: string;
    name: string;
    effect: string;         // 'attack' | 'affinity' | 'health_regen' | 'slot_upgrade' | 'defense' | 'element'
    value: number;
    slotCost: number;       // 1-3
}

export interface SafiAwakening {
    id: string;
    name: string;
    category: 'attack' | 'affinity' | 'sharpness' | 'slot' | 'element' | 'status' | 'skill' | 'set_bonus';
    tier: number;           // I-VI
    value: number;
    setBonusSet?: string;   // ex: "Teostra" for Teostra Essence
    skillRef?: SkillRef;    // if category is 'skill'
}

export interface CustomUpgrade {
    level: number;          // 1-7
    stat: 'attack' | 'affinity' | 'element' | 'defense';
    value: number;
}

// --- Build State ---

export interface EquipmentDecorations {
    weapon: (DecorationSlot | null)[];
    head: (DecorationSlot | null)[];
    chest: (DecorationSlot | null)[];
    arms: (DecorationSlot | null)[];
    waist: (DecorationSlot | null)[];
    legs: (DecorationSlot | null)[];
}

export interface BuildState {
    weapon: WeaponSlot | null;
    armor: Record<ArmorType, ArmorSlot | null>;
    charm: CharmSlot | null;
    decorations: EquipmentDecorations;
    weaponAugments: Augment[];
    safiAwakenings: (SafiAwakening | null)[];  // exactly 5 slots
    customUpgrades: CustomUpgrade[];
}

// --- Computed Stats ---

export interface SkillLevel {
    name: string;
    currentLevel: number;
    maxLevel: number;
    secretMaxLevel: number;   // max if secret is unlocked
    isSecretActive: boolean;
    sources: string[];        // where it comes from: "Elmo Kaiser γ+", "Ataque Joia 1", etc.
}

export interface SetBonus {
    setName: string;
    piecesEquipped: number;
    tiers: { piecesRequired: number; bonus: string; active: boolean }[];
}

export interface ComputedStats {
    trueRaw: number;
    displayAttack: number;
    affinity: number;
    effectiveAffinity: number;   // clamped to -100 ~ +100
    affinityBreakdown: {
        base: number;
        skills: number;          // static skills like Critical Eye
        conditional: number;     // conditional skills like Agitator, WEX
    };
    attackBreakdown: {
        base: number;
        skills: number;          // static skill raw
        conditional: number;     // conditional skill raw
    };
    efr: number;
    elementDamage: number;
    defense: number;
    activeSkills: SkillLevel[];
    activeSetBonuses: SetBonus[];
    skillSecrets: string[];       // which secrets are unlocked
    sharpnessColor: SharpnessColor;
}

// --- API Response Types ---

export interface WeaponListItem {
    id: number;
    name: string;
    name_en: string;
    type: string;
    rarity: number;
    attack: number;
    affinity: number;
    element: { type: string; damage: number } | null;
    slots: number[];
}

export interface ArmorListItem {
    id: number;
    name: string;
    type: ArmorType;
    rank: string;
    rarity: number;
    set_name: string;
    defense: { base: number; max: number };
    resistances: { fire: number; water: number; thunder: number; ice: number; dragon: number };
    slots: number[];
    skills: SkillRef[];
}

export interface DecorationListItem {
    id: number;
    name: string;
    tier: number;
    skill: SkillRef;
}

export interface CharmListItem {
    id: number;
    name: string;
    rarity: number;
    skills: SkillRef[];
}

export interface SetBonusListItem {
    set_name: string;
    pieces: { required: number; bonus_name: string; description: string }[];
}

// --- Saved Builds ---

export interface SavedBuild {
    id: string;
    name: string;
    createdAt: string;
    updatedAt: string;
    buildState: BuildState;
}
