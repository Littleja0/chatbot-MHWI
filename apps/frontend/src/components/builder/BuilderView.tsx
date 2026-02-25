import React, { useState, useCallback } from 'react';
import './Builder.css';
import { useBuildContext } from '../../contexts/BuildContext';
import EquipmentSlot from './EquipmentSlot';
import StatsPanel from './StatsPanel';
import EquipmentPicker, { PickerMode } from './EquipmentPicker';
import DecorationPicker from './DecorationPicker';
import BuildExporter from './BuildExporter';
import WeaponCustomizer from './WeaponCustomizer';
import { ArmorType } from '../../types/builder';
import { Sword, Shield, Shirt, Hand, CircleDot, Footprints, Link } from 'lucide-react';

const ARMOR_SLOTS: { type: ArmorType; label: string; icon: React.ReactNode }[] = [
    { type: 'head', label: 'Elmo', icon: <Shield size={20} /> },
    { type: 'chest', label: 'Peito', icon: <Shirt size={20} /> },
    { type: 'arms', label: 'Braços', icon: <Hand size={20} /> },
    { type: 'waist', label: 'Cintura', icon: <CircleDot size={20} /> },
    { type: 'legs', label: 'Pernas', icon: <Footprints size={20} /> },
];

interface PickerState {
    isOpen: boolean;
    mode: PickerMode;
    armorType?: string;
}

interface DecoPickerState {
    isOpen: boolean;
    equipSlot: string;       // 'weapon' | 'head' | 'chest' | ... | 'charm'
    decoIndex: number;
    maxTier: number;
}

const BuilderView: React.FC = () => {
    const { buildState, computedStats, dispatch } = useBuildContext();

    // Equipment Picker state
    const [picker, setPicker] = useState<PickerState>({ isOpen: false, mode: 'weapon' });

    // Decoration Picker state
    const [decoPicker, setDecoPicker] = useState<DecoPickerState>({
        isOpen: false, equipSlot: '', decoIndex: 0, maxTier: 1
    });

    const openPicker = useCallback((mode: PickerMode, armorType?: string) => {
        setPicker({ isOpen: true, mode, armorType });
    }, []);

    const handleEquipmentSelect = useCallback((item: any) => {
        if (picker.mode === 'weapon') {
            dispatch({
                type: 'SET_WEAPON', payload: {
                    id: item.id,
                    name: item.name,
                    namePt: item.name,
                    type: item.type,
                    rarity: item.rarity,
                    attack: item.attack,
                    attackTrue: item.attack_true,
                    affinity: item.affinity,
                    defense: item.defense || 0,
                    element: item.element ? { type: item.element.type, damage: item.element.damage, hidden: item.element.hidden } : undefined,
                    slots: item.slots || [],
                    sharpness: item.sharpness || '',
                    innateSkills: [],
                    armorsetBonusId: item.armorset_bonus_id,
                    category: item.category,
                }
            });
        } else if (picker.mode === 'armor' && picker.armorType) {
            dispatch({
                type: 'SET_ARMOR', payload: {
                    slot: picker.armorType as ArmorType,
                    piece: {
                        id: item.id,
                        name: item.name,
                        type: item.type,
                        rarity: item.rarity,
                        defense: item.defense?.base || 0,
                        resistances: item.resistances || {},
                        slots: item.slots || [],
                        skills: (item.skills || []).map((s: any) => ({ name: s.name, level: s.level })),
                        setId: item.armorset_id,
                        setName: item.set_name,
                    }
                }
            });
        } else if (picker.mode === 'charm') {
            dispatch({
                type: 'SET_CHARM', payload: {
                    id: item.id,
                    name: item.name,
                    rarity: item.rarity,
                    skills: (item.skills || []).map((s: any) => ({ name: s.name, level: s.level })),
                }
            });
        }
    }, [picker, dispatch]);

    const openDecoPicker = useCallback((equipSlot: string, decoIndex: number, maxTier: number) => {
        setDecoPicker({ isOpen: true, equipSlot, decoIndex, maxTier });
    }, []);

    const handleDecoSelect = useCallback((deco: any) => {
        const firstSkill = deco.skills?.[0] || { name: 'Unknown', level: 1 };
        dispatch({
            type: 'ADD_DECORATION',
            payload: {
                slot: decoPicker.equipSlot as keyof import('../../types/builder').EquipmentDecorations,
                index: decoPicker.decoIndex,
                decoration: {
                    id: deco.id,
                    name: deco.name,
                    tier: deco.tier,
                    rarity: deco.rarity,
                    skill: firstSkill,
                    skills: deco.skills || [],
                }
            }
        });
    }, [decoPicker, dispatch]);

    return (
        <div className="builder-view">
            {/* Left Column — Equipment Grid */}
            <div className="builder-equipment">
                <h2 className="builder-section-title">
                    <Sword size={20} />
                    Equipamento
                </h2>

                {/* Weapon Slot */}
                <EquipmentSlot
                    label="Arma"
                    icon={<Sword size={20} />}
                    piece={buildState.weapon}
                    slots={buildState.weapon?.slots || []}
                    skills={buildState.weapon?.innateSkills || []}
                    decorations={buildState.decorations.weapon}
                    onSelect={() => openPicker('weapon')}
                    onClear={() => dispatch({ type: 'SET_WEAPON', payload: null })}
                    onDecoClick={(idx, tier) => openDecoPicker('weapon', idx, tier)}
                    onDecoClear={(idx) => dispatch({ type: 'REMOVE_DECORATION', payload: { slot: 'weapon', index: idx } })}
                />

                {/* Weapon Customizer (Augments, Safi, Kulve) */}
                <WeaponCustomizer />

                {/* Armor Slots */}
                {ARMOR_SLOTS.map(({ type, label, icon }) => (
                    <EquipmentSlot
                        key={type}
                        label={label}
                        icon={icon}
                        piece={buildState.armor[type]}
                        slots={buildState.armor[type]?.slots || []}
                        skills={buildState.armor[type]?.skills || []}
                        decorations={buildState.decorations[type]}
                        onSelect={() => openPicker('armor', type)}
                        onClear={() => dispatch({ type: 'SET_ARMOR', payload: { slot: type, piece: null } })}
                        onDecoClick={(idx, tier) => openDecoPicker(type, idx, tier)}
                        onDecoClear={(idx) => dispatch({ type: 'REMOVE_DECORATION', payload: { slot: type, index: idx } })}
                    />
                ))}

                {/* Charm Slot */}
                <EquipmentSlot
                    label="Amuleto"
                    icon={<Link size={20} />}
                    piece={buildState.charm}
                    slots={[]}
                    skills={buildState.charm?.skills || []}
                    onSelect={() => openPicker('charm')}
                    onClear={() => dispatch({ type: 'SET_CHARM', payload: null })}
                />

                {/* Build Exporter */}
                <BuildExporter />
            </div>

            {/* Right Column — Summary Cards */}
            <div className="builder-summary">
                <StatsPanel stats={computedStats} />
            </div>

            {/* Equipment Picker Modal */}
            <EquipmentPicker
                mode={picker.mode}
                armorType={picker.armorType}
                isOpen={picker.isOpen}
                onClose={() => setPicker(p => ({ ...p, isOpen: false }))}
                onSelect={handleEquipmentSelect}
            />

            {/* Decoration Picker Modal */}
            <DecorationPicker
                isOpen={decoPicker.isOpen}
                maxTier={decoPicker.maxTier}
                onClose={() => setDecoPicker(p => ({ ...p, isOpen: false }))}
                onSelect={handleDecoSelect}
            />
        </div>
    );
};

export default BuilderView;
