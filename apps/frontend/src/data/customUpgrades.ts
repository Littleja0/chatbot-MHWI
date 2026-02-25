/**
 * Kulve Taroth Custom Upgrades (7 levels)
 *
 * Taroth weapons (non-Kjarr) can be customized with incremental stat upgrades.
 * Each level provides a fixed bonus.
 *
 * Source: MHW:I community data
 */

import { CustomUpgrade } from '../types/builder';

export interface CustomUpgradeTemplate {
    stat: CustomUpgrade['stat'];
    label: string;
    levels: { level: number; value: number }[];
}

export const CUSTOM_UPGRADE_TEMPLATES: CustomUpgradeTemplate[] = [
    {
        stat: 'attack',
        label: 'Ataque',
        levels: [
            { level: 1, value: 5 },
            { level: 2, value: 5 },
            { level: 3, value: 5 },
            { level: 4, value: 5 },
            { level: 5, value: 5 },
            { level: 6, value: 5 },
            { level: 7, value: 5 },
        ],
    },
    {
        stat: 'affinity',
        label: 'Afinidade',
        levels: [
            { level: 1, value: 2 },
            { level: 2, value: 2 },
            { level: 3, value: 2 },
            { level: 4, value: 2 },
            { level: 5, value: 2 },
            { level: 6, value: 2 },
            { level: 7, value: 2 },
        ],
    },
    {
        stat: 'element',
        label: 'Elemento',
        levels: [
            { level: 1, value: 10 },
            { level: 2, value: 10 },
            { level: 3, value: 10 },
            { level: 4, value: 10 },
            { level: 5, value: 10 },
            { level: 6, value: 10 },
            { level: 7, value: 10 },
        ],
    },
    {
        stat: 'defense',
        label: 'Defesa',
        levels: [
            { level: 1, value: 5 },
            { level: 2, value: 5 },
            { level: 3, value: 5 },
            { level: 4, value: 5 },
            { level: 5, value: 5 },
            { level: 6, value: 5 },
            { level: 7, value: 5 },
        ],
    },
];
