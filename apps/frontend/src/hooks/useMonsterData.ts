
import { useChatContext } from '../contexts/ChatContext';
import { MonsterIntel } from '../types';

/**
 * Hook para dados de monstro detectado na conversa.
 */
export function useMonsterData(): MonsterIntel | null {
    const { monsterIntel } = useChatContext();
    return monsterIntel;
}
