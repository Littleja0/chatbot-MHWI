import { useState, useEffect, useCallback } from 'react';
import { BuildState, SavedBuild } from '../types/builder';

const STORAGE_KEY = 'mhwi-saved-builds';
const MAX_BUILDS = 50;

function readFromStorage(): SavedBuild[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return [];
        return JSON.parse(raw) as SavedBuild[];
    } catch {
        console.warn('[useSavedBuilds] Failed to read from localStorage');
        return [];
    }
}

function writeToStorage(builds: SavedBuild[]): void {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(builds));
    } catch (e) {
        console.error('[useSavedBuilds] Failed to write to localStorage', e);
    }
}

export function useSavedBuilds() {
    const [savedBuilds, setSavedBuilds] = useState<SavedBuild[]>(() => readFromStorage());

    // Sync state → localStorage whenever it changes
    useEffect(() => {
        writeToStorage(savedBuilds);
    }, [savedBuilds]);

    const saveBuild = useCallback((name: string, state: BuildState) => {
        setSavedBuilds(prev => {
            if (prev.length >= MAX_BUILDS) return prev; // at limit
            const now = new Date().toISOString();
            const newBuild: SavedBuild = {
                id: crypto.randomUUID(),
                name: name.trim() || 'Build sem nome',
                createdAt: now,
                updatedAt: now,
                buildState: structuredClone(state),
            };
            return [newBuild, ...prev];
        });
    }, []);

    const loadBuild = useCallback((id: string): BuildState | null => {
        const build = savedBuilds.find(b => b.id === id);
        return build ? structuredClone(build.buildState) : null;
    }, [savedBuilds]);

    const deleteBuild = useCallback((id: string) => {
        setSavedBuilds(prev => prev.filter(b => b.id !== id));
    }, []);

    const renameBuild = useCallback((id: string, newName: string) => {
        setSavedBuilds(prev =>
            prev.map(b =>
                b.id === id
                    ? { ...b, name: newName.trim() || b.name, updatedAt: new Date().toISOString() }
                    : b
            )
        );
    }, []);

    const isAtLimit = savedBuilds.length >= MAX_BUILDS;

    return { savedBuilds, saveBuild, loadBuild, deleteBuild, renameBuild, isAtLimit };
}
