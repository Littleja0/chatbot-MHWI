/**
 * buildHelpers.ts — Utility functions for the Build Builder.
 */

const PREPOSITIONS = new Set(['de', 'a', 'do', 'da', 'em', 'e', 'ao', 'à', 'os', 'as', 'o']);

/**
 * Abbreviate a skill name for display in jewel slots.
 * Rules:
 * - Filter out Portuguese prepositions (de, a, do, da, em, ...)
 * - Take first letter of each significant word (up to 3 chars)
 * - If only 1 word remains, take first 2 letters
 *
 * Examples:
 *   "Reforço de Ataque" → "RA"
 *   "Olho Crítico" → "OC"
 *   "Exploração de Fraqueza" → "EF"
 *   "Agitador" → "Ag"
 *   "Resistência a Fogo" → "RF"
 */
export function abbreviateSkill(skillName: string): string {
    if (!skillName) return '?';

    const words = skillName.split(/\s+/).filter(w => !PREPOSITIONS.has(w.toLowerCase()));

    if (words.length === 0) return skillName.charAt(0).toUpperCase();
    if (words.length === 1) return words[0].substring(0, 2);

    // Take first letter of each significant word (max 3)
    return words
        .slice(0, 3)
        .map(w => w.charAt(0).toUpperCase())
        .join('');
}

/**
 * Format a relative time string from an ISO date.
 * e.g., "há 2 horas", "há 3 dias"
 */
export function formatRelativeTime(isoDate: string): string {
    const now = Date.now();
    const then = new Date(isoDate).getTime();
    const diffMs = now - then;

    const minutes = Math.floor(diffMs / 60000);
    const hours = Math.floor(diffMs / 3600000);
    const days = Math.floor(diffMs / 86400000);

    if (minutes < 1) return 'agora';
    if (minutes < 60) return `há ${minutes}min`;
    if (hours < 24) return `há ${hours}h`;
    if (days < 30) return `há ${days}d`;
    return new Date(isoDate).toLocaleDateString('pt-BR');
}
