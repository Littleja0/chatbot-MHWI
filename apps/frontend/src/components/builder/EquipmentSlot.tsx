import React from 'react';
import { X, ChevronRight } from 'lucide-react';
import { SkillRef } from '../../types/builder';

const TIER_COLORS: Record<number, string> = {
    1: '#888',       // cinza
    2: '#4ade80',    // verde
    3: '#60a5fa',    // azul
    4: '#fbbf24',    // dourado
};

interface EquipmentSlotProps {
    label: string;
    icon: React.ReactNode;
    piece: { name: string;[key: string]: any } | null;
    slots: number[];
    skills: SkillRef[];
    decorations?: (any | null)[];
    onSelect: () => void;
    onClear: () => void;
    onDecoClick?: (index: number, maxTier: number) => void;
    onDecoClear?: (index: number) => void;
}

const EquipmentSlot: React.FC<EquipmentSlotProps> = ({
    label,
    icon,
    piece,
    slots,
    skills,
    decorations,
    onSelect,
    onClear,
    onDecoClick,
    onDecoClear,
}) => {
    return (
        <div className={`equipment-slot ${piece ? 'equipment-slot--filled' : 'equipment-slot--empty'}`}>
            <div className="equipment-slot__header" onClick={onSelect}>
                <div className="equipment-slot__icon">
                    {icon}
                </div>
                <div className="equipment-slot__info">
                    <span className="equipment-slot__label">{label}</span>
                    <span className="equipment-slot__name">
                        {piece ? piece.name : `Selecionar ${label}`}
                    </span>
                </div>
                <div className="equipment-slot__actions">
                    {piece ? (
                        <button
                            className="equipment-slot__clear"
                            onClick={(e) => { e.stopPropagation(); onClear(); }}
                            title="Remover"
                        >
                            <X size={14} />
                        </button>
                    ) : (
                        <ChevronRight size={18} className="text-gray-500" />
                    )}
                </div>
            </div>

            {/* Decoration Slots */}
            {piece && slots.length > 0 && (
                <div className="equipment-slot__deco-row">
                    {slots.map((tier, i) => {
                        const deco = decorations?.[i];
                        return (
                            <button
                                key={i}
                                className={`deco-slot ${deco ? 'deco-slot--filled' : ''}`}
                                style={{ borderColor: TIER_COLORS[deco?.tier || tier] || '#555' }}
                                title={deco ? `${deco.name} (Tier ${deco.tier})` : `Slot Nível ${tier} — Clique para adicionar`}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (deco) return; // Already filled — right-click to remove
                                    onDecoClick?.(i, tier);
                                }}
                                onContextMenu={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    if (deco) onDecoClear?.(i);
                                }}
                            >
                                {deco ? (
                                    <span
                                        className="deco-slot__diamond"
                                        style={{ backgroundColor: TIER_COLORS[deco.tier] || '#555' }}
                                    />
                                ) : (
                                    <span
                                        className="deco-slot__diamond"
                                        style={{ backgroundColor: TIER_COLORS[tier] || '#555', opacity: 0.3 }}
                                    />
                                )}
                            </button>
                        );
                    })}
                </div>
            )}

            {/* Skills */}
            {piece && skills.length > 0 && (
                <div className="equipment-slot__skills">
                    {skills.map((s, i) => (
                        <span key={i} className="equipment-slot__skill-tag">
                            {s.name} Lv{s.level}
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
};

export default EquipmentSlot;
