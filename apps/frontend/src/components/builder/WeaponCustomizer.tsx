import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronRight, Plus, X, Zap, Sparkles, Wrench } from 'lucide-react';
import { useBuildContext } from '../../contexts/BuildContext';
import { Augment, SafiAwakening, CustomUpgrade } from '../../types/builder';
import { AUGMENT_TEMPLATES, AUGMENT_SLOT_LIMITS, getRemainingAugmentSlots } from '../../data/augmentations';
import { SAFI_AWAKENINGS, getSafiAwakeningsByCategory } from '../../data/safiAwakenings';
import { CUSTOM_UPGRADE_TEMPLATES } from '../../data/customUpgrades';

// ============================================================
// Collapsible Section
// ============================================================

interface SectionProps {
    title: string;
    icon: React.ReactNode;
    accentColor: string;
    children: React.ReactNode;
    isEmpty?: boolean;
}

const CollapsibleSection: React.FC<SectionProps> = ({ title, icon, accentColor, children, isEmpty }) => {
    const [open, setOpen] = useState(false);
    return (
        <div className="wcust-section" style={{ borderColor: open ? accentColor : undefined }}>
            <button className="wcust-section__toggle" onClick={() => setOpen(!open)}>
                <span className="wcust-section__icon" style={{ color: accentColor }}>{icon}</span>
                <span className="wcust-section__title">{title}</span>
                {isEmpty && <span className="wcust-section__badge">Vazio</span>}
                {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
            {open && <div className="wcust-section__body">{children}</div>}
        </div>
    );
};

// ============================================================
// Augments Section
// ============================================================

const AugmentsSection: React.FC = () => {
    const { buildState, dispatch } = useBuildContext();
    const weapon = buildState.weapon;
    const rarity = weapon?.rarity || 12;
    const augments = buildState.weaponAugments;
    const remaining = getRemainingAugmentSlots(rarity, augments);
    const maxSlots = AUGMENT_SLOT_LIMITS[rarity] || 3;

    const addAugment = (template: Augment) => {
        if (template.slotCost > remaining) return;
        dispatch({ type: 'SET_AUGMENTS', payload: [...augments, { ...template, id: `${template.id}-${Date.now()}` }] });
    };

    const removeAugment = (index: number) => {
        const next = [...augments];
        next.splice(index, 1);
        dispatch({ type: 'SET_AUGMENTS', payload: next });
    };

    return (
        <div className="wcust-aug">
            <div className="wcust-aug__info">
                Slots: <strong>{maxSlots - remaining}</strong> / {maxSlots} usados
                <span className="wcust-aug__remaining">{remaining} restante{remaining !== 1 ? 's' : ''}</span>
            </div>

            {/* Current augments */}
            {augments.length > 0 && (
                <div className="wcust-aug__list">
                    {augments.map((aug, i) => (
                        <div key={i} className="wcust-aug__item">
                            <span className="wcust-aug__name">{aug.name}</span>
                            <span className="wcust-aug__cost">({aug.slotCost} slot{aug.slotCost > 1 ? 's' : ''})</span>
                            <button className="wcust-aug__remove" onClick={() => removeAugment(i)} title="Remover">
                                <X size={12} />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Add augment buttons */}
            {remaining > 0 && (
                <div className="wcust-aug__add-grid">
                    {AUGMENT_TEMPLATES.filter(t => t.slotCost <= remaining).map(template => (
                        <button
                            key={template.id}
                            className="wcust-aug__add-btn"
                            onClick={() => addAugment(template)}
                            title={`${template.name} (Custo: ${template.slotCost})`}
                        >
                            <Plus size={12} />
                            <span>{template.name}</span>
                            <span className="wcust-aug__add-cost">{template.slotCost}</span>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

// ============================================================
// Safi Awakenings Section
// ============================================================

const SAFI_CATEGORIES = [
    { key: 'attack', label: 'Ataque' },
    { key: 'affinity', label: 'Afinidade' },
    { key: 'sharpness', label: 'Sharpness' },
    { key: 'element', label: 'Elemento' },
    { key: 'slot', label: 'Slot' },
    { key: 'set_bonus', label: 'Essência' },
];

const SafiSection: React.FC = () => {
    const { buildState, dispatch } = useBuildContext();
    const awakenings = buildState.safiAwakenings;
    const [activeSlot, setActiveSlot] = useState<number | null>(null);
    const [filterCat, setFilterCat] = useState<string>('attack');

    const filteredAwakenings = useMemo(() =>
        getSafiAwakeningsByCategory(filterCat), [filterCat]);

    const setAwakening = (slotIndex: number, awakening: SafiAwakening | null) => {
        dispatch({ type: 'SET_SAFI_AWAKENING', payload: { index: slotIndex, awakening } });
        setActiveSlot(null);
    };

    return (
        <div className="wcust-safi">
            {/* 5 awakening slots */}
            <div className="wcust-safi__slots">
                {awakenings.map((awk, i) => (
                    <button
                        key={i}
                        className={`wcust-safi__slot ${awk ? 'wcust-safi__slot--filled' : ''} ${activeSlot === i ? 'wcust-safi__slot--active' : ''}`}
                        onClick={() => setActiveSlot(activeSlot === i ? null : i)}
                    >
                        {awk ? (
                            <>
                                <span className="wcust-safi__slot-name">{awk.name}</span>
                                <button
                                    className="wcust-safi__slot-clear"
                                    onClick={e => { e.stopPropagation(); setAwakening(i, null); }}
                                >
                                    <X size={10} />
                                </button>
                            </>
                        ) : (
                            <span className="wcust-safi__slot-empty">Slot {i + 1}</span>
                        )}
                    </button>
                ))}
            </div>

            {/* Selection panel (when a slot is active) */}
            {activeSlot !== null && (
                <div className="wcust-safi__picker">
                    <div className="wcust-safi__cats">
                        {SAFI_CATEGORIES.map(cat => (
                            <button
                                key={cat.key}
                                className={`wcust-safi__cat ${filterCat === cat.key ? 'wcust-safi__cat--active' : ''}`}
                                onClick={() => setFilterCat(cat.key)}
                            >
                                {cat.label}
                            </button>
                        ))}
                    </div>
                    <div className="wcust-safi__options">
                        {filteredAwakenings.map(awk => (
                            <button
                                key={awk.id}
                                className="wcust-safi__option"
                                onClick={() => setAwakening(activeSlot, awk)}
                            >
                                <span>{awk.name}</span>
                                {awk.value > 0 && <span className="wcust-safi__option-val">+{awk.value}</span>}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

// ============================================================
// Custom Upgrades Section (Kulve Taroth)
// ============================================================

const CustomUpgradesSection: React.FC = () => {
    const { buildState, dispatch } = useBuildContext();
    const upgrades = buildState.customUpgrades;

    const addUpgradeLevel = (stat: CustomUpgrade['stat'], value: number) => {
        const currentLevels = upgrades.filter(u => u.stat === stat).length;
        if (currentLevels >= 7) return;
        const newUpgrade: CustomUpgrade = { level: currentLevels + 1, stat, value };
        dispatch({ type: 'SET_CUSTOM_UPGRADES', payload: [...upgrades, newUpgrade] });
    };

    const removeLastOfStat = (stat: string) => {
        const idx = [...upgrades].reverse().findIndex(u => u.stat === stat);
        if (idx === -1) return;
        const realIdx = upgrades.length - 1 - idx;
        const next = [...upgrades];
        next.splice(realIdx, 1);
        dispatch({ type: 'SET_CUSTOM_UPGRADES', payload: next });
    };

    return (
        <div className="wcust-custom">
            {CUSTOM_UPGRADE_TEMPLATES.map(template => {
                const count = upgrades.filter(u => u.stat === template.stat).length;
                const nextLevel = template.levels[count];
                return (
                    <div key={template.stat} className="wcust-custom__row">
                        <span className="wcust-custom__label">{template.label}</span>
                        <div className="wcust-custom__bar">
                            {template.levels.map((lvl, i) => (
                                <div
                                    key={i}
                                    className={`wcust-custom__seg ${i < count ? 'wcust-custom__seg--filled' : ''}`}
                                    title={`Lv${lvl.level}: +${lvl.value}`}
                                />
                            ))}
                        </div>
                        <span className="wcust-custom__count">Lv{count}/7</span>
                        <button
                            className="wcust-custom__btn"
                            onClick={() => removeLastOfStat(template.stat)}
                            disabled={count === 0}
                            title="Remover nível"
                        >−</button>
                        <button
                            className="wcust-custom__btn wcust-custom__btn--add"
                            onClick={() => nextLevel && addUpgradeLevel(template.stat, nextLevel.value)}
                            disabled={count >= 7}
                            title="Adicionar nível"
                        >+</button>
                    </div>
                );
            })}
        </div>
    );
};

// ============================================================
// Main Component
// ============================================================

const WeaponCustomizer: React.FC = () => {
    const { buildState } = useBuildContext();
    const weapon = buildState.weapon;

    if (!weapon) return null;

    // Determine which sections to show
    const isSafi = weapon.isSafi || weapon.name?.toLowerCase().includes('safi');
    const isKulve = weapon.isCustomizable || weapon.name?.toLowerCase().includes('taroth');
    const showAugments = true; // All MR weapons can be augmented

    // If no customization options, don't render
    if (!isSafi && !isKulve && !showAugments) return null;

    return (
        <div className="wcust">
            {showAugments && (
                <CollapsibleSection
                    title="Augmentações"
                    icon={<Wrench size={16} />}
                    accentColor="#60a5fa"
                    isEmpty={buildState.weaponAugments.length === 0}
                >
                    <AugmentsSection />
                </CollapsibleSection>
            )}

            {isSafi && (
                <CollapsibleSection
                    title="Safi Awakenings"
                    icon={<Sparkles size={16} />}
                    accentColor="#f59e0b"
                    isEmpty={buildState.safiAwakenings.every(a => a === null)}
                >
                    <SafiSection />
                </CollapsibleSection>
            )}

            {isKulve && (
                <CollapsibleSection
                    title="Custom Upgrades"
                    icon={<Zap size={16} />}
                    accentColor="#a855f7"
                    isEmpty={buildState.customUpgrades.length === 0}
                >
                    <CustomUpgradesSection />
                </CollapsibleSection>
            )}
        </div>
    );
};

export default WeaponCustomizer;
