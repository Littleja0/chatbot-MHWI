/**
 * Sharpness Multipliers for Raw and Elemental damage.
 * Source: https://monsterhunterworld.wiki.fextralife.com/Sharpness
 */

import { SharpnessColor } from '../types/builder';

export const SHARPNESS_RAW_MULTIPLIERS: Record<SharpnessColor, number> = {
    red: 0.50,
    orange: 0.75,
    yellow: 1.00,
    green: 1.05,
    blue: 1.20,
    white: 1.32,
    purple: 1.39,
};

export const SHARPNESS_ELEMENT_MULTIPLIERS: Record<SharpnessColor, number> = {
    red: 0.25,
    orange: 0.50,
    yellow: 0.75,
    green: 1.00,
    blue: 1.0625,
    white: 1.15,
    purple: 1.25,
};
