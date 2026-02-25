/**
 * Safi'jiiva Awakened Abilities Lookup
 *
 * Each Safi weapon has 5 awakening slots.
 * Source: MHW:I community data
 */

import { SafiAwakening } from '../types/builder';

export const SAFI_AWAKENINGS: SafiAwakening[] = [
    // --- Attack ---
    { id: 'atk-1', name: 'Attack Increase I', category: 'attack', tier: 1, value: 6 },
    { id: 'atk-2', name: 'Attack Increase II', category: 'attack', tier: 2, value: 8 },
    { id: 'atk-3', name: 'Attack Increase III', category: 'attack', tier: 3, value: 10 },
    { id: 'atk-4', name: 'Attack Increase IV', category: 'attack', tier: 4, value: 12 },
    { id: 'atk-5', name: 'Attack Increase V', category: 'attack', tier: 5, value: 15 },
    { id: 'atk-6', name: 'Attack Increase VI', category: 'attack', tier: 6, value: 20 },

    // --- Affinity ---
    { id: 'aff-1', name: 'Affinity Increase I', category: 'affinity', tier: 1, value: 5 },
    { id: 'aff-2', name: 'Affinity Increase II', category: 'affinity', tier: 2, value: 5 },
    { id: 'aff-3', name: 'Affinity Increase III', category: 'affinity', tier: 3, value: 8 },
    { id: 'aff-4', name: 'Affinity Increase IV', category: 'affinity', tier: 4, value: 10 },
    { id: 'aff-5', name: 'Affinity Increase V', category: 'affinity', tier: 5, value: 10 },
    { id: 'aff-6', name: 'Affinity Increase VI', category: 'affinity', tier: 6, value: 15 },

    // --- Sharpness ---
    { id: 'sharp-1', name: 'Sharpness Increase I', category: 'sharpness', tier: 1, value: 10 },
    { id: 'sharp-2', name: 'Sharpness Increase II', category: 'sharpness', tier: 2, value: 20 },
    { id: 'sharp-3', name: 'Sharpness Increase III', category: 'sharpness', tier: 3, value: 30 },
    { id: 'sharp-4', name: 'Sharpness Increase IV', category: 'sharpness', tier: 4, value: 40 },
    { id: 'sharp-5', name: 'Sharpness Increase V', category: 'sharpness', tier: 5, value: 50 },
    { id: 'sharp-6', name: 'Sharpness Increase VI', category: 'sharpness', tier: 6, value: 70 },

    // --- Slot Upgrade ---
    { id: 'slot-1', name: 'Slot Upgrade I', category: 'slot', tier: 1, value: 1 },
    { id: 'slot-2', name: 'Slot Upgrade II', category: 'slot', tier: 2, value: 2 },
    { id: 'slot-3', name: 'Slot Upgrade III', category: 'slot', tier: 3, value: 3 },

    // --- Element ---
    { id: 'elem-1', name: 'Element/Status I', category: 'element', tier: 1, value: 30 },
    { id: 'elem-2', name: 'Element/Status II', category: 'element', tier: 2, value: 50 },
    { id: 'elem-3', name: 'Element/Status III', category: 'element', tier: 3, value: 60 },
    { id: 'elem-4', name: 'Element/Status IV', category: 'element', tier: 4, value: 80 },
    { id: 'elem-5', name: 'Element/Status V', category: 'element', tier: 5, value: 100 },
    { id: 'elem-6', name: 'Element/Status VI', category: 'element', tier: 6, value: 150 },

    // --- Set Bonus Essences ---
    { id: 'teo-ess', name: 'Teostra Essence', category: 'set_bonus', tier: 5, value: 0, setBonusSet: 'Teostra Technique' },
    { id: 'nami-ess', name: 'Namielle Essence', category: 'set_bonus', tier: 5, value: 0, setBonusSet: 'Namielle Divinity' },
    { id: 'velk-ess', name: 'Velkhana Essence', category: 'set_bonus', tier: 5, value: 0, setBonusSet: 'Velkhana Divinity' },
    { id: 'brach-ess', name: 'Brachydios Essence', category: 'set_bonus', tier: 5, value: 0, setBonusSet: 'Raging Brachydios Mastery' },
    { id: 'zorah-ess', name: 'Zorah Essence', category: 'set_bonus', tier: 5, value: 0, setBonusSet: 'Zorah Magdaros Mastery' },
    { id: 'nerg-ess', name: 'Nergigante Essence', category: 'set_bonus', tier: 5, value: 0, setBonusSet: 'Ruiner Nergigante Hunger' },
];

// Filter helpers
export const getSafiAwakeningsByCategory = (category: string) =>
    SAFI_AWAKENINGS.filter(a => a.category === category);

export const getSafiEssences = () =>
    SAFI_AWAKENINGS.filter(a => a.category === 'set_bonus');
