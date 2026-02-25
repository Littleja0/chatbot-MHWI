/**
 * buildSerializer.ts — Serializes build state to JSON and readable text.
 */

import { BuildState, ComputedStats, ArmorType, SkillLevel } from '../types/builder';
import { WEAPON_MULTIPLIERS } from '../data/weaponMultipliers';

/**
 * Serialize build to a structured JSON object for the AI.
 */
export function serializeBuildToJSON(state: BuildState, stats: ComputedStats): Record<string, any> {
    const weapon = state.weapon ? {
        name: state.weapon.name,
        type: state.weapon.type,
        rarity: state.weapon.rarity,
        attack: state.weapon.attack,
        attack_true: stats.trueRaw,
        affinity: state.weapon.affinity,
        element: state.weapon.element,
        slots: state.weapon.slots,
    } : null;

    const armor: Record<string, any> = {};
    for (const type of ['head', 'chest', 'arms', 'waist', 'legs'] as ArmorType[]) {
        const piece = state.armor[type];
        if (piece) {
            armor[type] = {
                name: piece.name,
                skills: piece.skills,
                slots: piece.slots,
            };
        }
    }

    const charm = state.charm ? {
        name: state.charm.name,
        skills: state.charm.skills,
    } : null;

    const decorations: string[] = [];
    for (const [, decos] of Object.entries(state.decorations)) {
        decos.forEach(d => {
            if (d) decorations.push(`${d.name} (Tier ${d.tier})`);
        });
    }

    return {
        weapon,
        armor,
        charm,
        decorations,
        stats: {
            true_raw: stats.trueRaw,
            display_attack: stats.displayAttack,
            affinity: `${stats.affinity}%`,
            efr: stats.efr,
            element_damage: stats.elementDamage,
            defense: stats.defense,
            sharpness: stats.sharpnessColor,
        },
        active_skills: stats.activeSkills.map(s => ({
            name: s.name,
            level: `${s.currentLevel}/${s.maxLevel || '?'}`,
        })),
    };
}

/**
 * Convert build to readable text for chat display.
 */
export function buildToReadableText(state: BuildState, stats: ComputedStats): string {
    const lines: string[] = ['🛡️ **Build Exportada**\n'];

    // Weapon
    if (state.weapon) {
        lines.push(`⚔️ **Arma:** ${state.weapon.name}`);
        lines.push(`   Ataque: ${stats.displayAttack} (True Raw: ${stats.trueRaw})`);
        lines.push(`   Afinidade: ${stats.affinity}%`);
        if (state.weapon.element) {
            lines.push(`   Elemento: ${state.weapon.element.type} ${stats.elementDamage}`);
        }
        lines.push(`   Sharpness: ${stats.sharpnessColor}`);
    }

    // Armor
    const armorLabels: Record<string, string> = {
        head: '🪖 Elmo', chest: '🛡️ Peito', arms: '🧤 Braços',
        waist: '🩲 Cintura', legs: '🥾 Pernas',
    };
    for (const type of ['head', 'chest', 'arms', 'waist', 'legs'] as ArmorType[]) {
        const piece = state.armor[type];
        if (piece) {
            const skillText = piece.skills.map(s => `${s.name} Lv${s.level}`).join(', ');
            lines.push(`${armorLabels[type]}: ${piece.name} [${skillText}]`);
        }
    }

    // Charm
    if (state.charm) {
        const skillText = state.charm.skills.map(s => `${s.name} Lv${s.level}`).join(', ');
        lines.push(`📿 **Amuleto:** ${state.charm.name} [${skillText}]`);
    }

    // Decorations
    const decos: string[] = [];
    for (const [, slotDecos] of Object.entries(state.decorations)) {
        slotDecos.forEach(d => {
            if (d) decos.push(d.name);
        });
    }
    if (decos.length > 0) {
        lines.push(`\n💎 **Joias:** ${decos.join(', ')}`);
    }

    // Stats
    lines.push('\n📊 **Estatísticas**');
    lines.push(`   EFR: **${stats.efr}**`);
    lines.push(`   True Raw: ${stats.trueRaw} | Display: ${stats.displayAttack}`);
    lines.push(`   Afinidade: ${stats.affinity}%`);
    lines.push(`   Defesa: ${stats.defense}`);

    // Active Skills
    if (stats.activeSkills.length > 0) {
        lines.push('\n🔥 **Skills Ativas:**');
        stats.activeSkills
            .filter(s => s.currentLevel > 0)
            .sort((a, b) => b.currentLevel - a.currentLevel)
            .forEach(s => {
                lines.push(`   ${s.name}: Lv${s.currentLevel}`);
            });
    }

    return lines.join('\n');
}
