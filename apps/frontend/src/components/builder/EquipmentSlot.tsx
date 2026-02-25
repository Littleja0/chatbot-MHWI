import React from 'react';
import { X, ChevronRight } from 'lucide-react';
import { SkillRef } from '../../types/builder';
import { abbreviateSkill } from '../../utils/buildHelpers';

const TIER_COLORS: Record<number, string> = {
    1: '#888',       // cinza
    2: '#4ade80',    // verde
    3: '#60a5fa',    // azul
    4: '#fbbf24',    // dourado
};

const TIER_BG_COLORS: Record<number, string> = {
    1: 'rgba(136, 136, 136, 0.2)',
    2: 'rgba(74, 222, 128, 0.2)',
    3: 'rgba(96, 165, 250, 0.2)',
    4: 'rgba(251, 191, 36, 0.2)',
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
                        const decoSkills: SkillRef[] = deco?.skills || (deco?.skill ? [deco.skill] : []);
                        const primarySkill = decoSkills[0];
                        const abbr = primarySkill ? abbreviateSkill(primarySkill.name) : '';

                        return (
                            <button
                                key={i}
                                className={`deco-slot ${deco ? 'deco-slot--filled' : ''}`}
                                style={{ borderColor: TIER_COLORS[deco?.tier || tier] || '#555' }}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (deco) return;
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
                                        className="deco-slot__jewel-icon"
                                        style={{
                                            borderColor: TIER_COLORS[deco.tier] || '#555',
                                            backgroundColor: TIER_BG_COLORS[deco.tier] || 'rgba(85,85,85,0.2)',
                                        }}
                                    >
                                        <span className="deco-slot__jewel-abbr">{abbr}</span>
                                    </span>
                                ) : (
                                    <span
                                        className="deco-slot__diamond"
                                        style={{ backgroundColor: TIER_COLORS[tier] || '#555', opacity: 0.3 }}
                                    />
                                )}

                                {/* Tooltip */}
                                {deco && decoSkills.length > 0 && (
                                    <div className="deco-tooltip" style={{ borderColor: TIER_COLORS[deco.tier] || '#555' }}>
                                        <div className="deco-tooltip__name">{deco.name}</div>
                                        {decoSkills.map((s: SkillRef, si: number) => (
                                            <div key={si} className="deco-tooltip__skill">
                                                <div className="deco-tooltip__skill-name">
                                                    {s.name} <span className="deco-tooltip__skill-level">+{s.level}</span>
                                                </div>
                                                {s.description && (
                                                    <div className="deco-tooltip__skill-desc">{s.description}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
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
