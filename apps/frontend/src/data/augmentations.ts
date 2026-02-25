/**
 * Weapon Augmentations Lookup
 *
 * Available augment slots by rarity:
 *   R10: 5 slots, R11: 4 slots, R12: 3 slots
 *
 * Source: MHW:I community data
 */

import { Augment } from '../types/builder';

export const AUGMENT_TEMPLATES: Augment[] = [
    { id: 'aug-atk-1', name: 'Attack Increase', effect: 'attack', value: 5, slotCost: 1 },
    { id: 'aug-atk-2', name: 'Attack Increase II', effect: 'attack', value: 5, slotCost: 2 },
    { id: 'aug-atk-3', name: 'Attack Increase III', effect: 'attack', value: 5, slotCost: 3 },

    { id: 'aug-aff-1', name: 'Affinity Increase', effect: 'affinity', value: 10, slotCost: 1 },
    { id: 'aug-aff-2', name: 'Affinity Increase II', effect: 'affinity', value: 10, slotCost: 2 },
    { id: 'aug-aff-3', name: 'Affinity Increase III', effect: 'affinity', value: 10, slotCost: 3 },

    { id: 'aug-def-1', name: 'Defense Increase', effect: 'defense', value: 10, slotCost: 1 },
    { id: 'aug-def-2', name: 'Defense Increase II', effect: 'defense', value: 10, slotCost: 2 },
    { id: 'aug-def-3', name: 'Defense Increase III', effect: 'defense', value: 10, slotCost: 3 },

    { id: 'aug-health-1', name: 'Health Regen', effect: 'health_regen', value: 1, slotCost: 1 },
    { id: 'aug-health-2', name: 'Health Regen II', effect: 'health_regen', value: 1, slotCost: 2 },
    { id: 'aug-health-3', name: 'Health Regen III', effect: 'health_regen', value: 1, slotCost: 3 },

    { id: 'aug-slot-1', name: 'Slot Upgrade', effect: 'slot_upgrade', value: 1, slotCost: 3 },

    { id: 'aug-elem-1', name: 'Element/Status Up', effect: 'element', value: 30, slotCost: 1 },
    { id: 'aug-elem-2', name: 'Element/Status Up II', effect: 'element', value: 30, slotCost: 2 },
    { id: 'aug-elem-3', name: 'Element/Status Up III', effect: 'element', value: 30, slotCost: 3 },
];

/**
 * Maximum augment slots by weapon rarity.
 */
export const AUGMENT_SLOT_LIMITS: Record<number, number> = {
    10: 5,
    11: 4,
    12: 3,
};

/**
 * Get available augment slots remaining.
 */
export function getRemainingAugmentSlots(rarity: number, currentAugments: Augment[]): number {
    const maxSlots = AUGMENT_SLOT_LIMITS[rarity] || 3;
    const usedSlots = currentAugments.reduce((sum, a) => sum + a.slotCost, 0);
    return maxSlots - usedSlots;
}
