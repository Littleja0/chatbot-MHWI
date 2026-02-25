import React, { useState, useEffect, useMemo } from 'react';
import { Search, X, ChevronDown, Loader2 } from 'lucide-react';
import { getWeapons, getArmor, getCharms } from '../../services/apiService';

export type PickerMode = 'weapon' | 'armor' | 'charm';

interface EquipmentPickerProps {
    mode: PickerMode;
    armorType?: string;        // head, chest, arms, waist, legs
    isOpen: boolean;
    onClose: () => void;
    onSelect: (item: any) => void;
}

const WEAPON_TYPES = [
    { value: '', label: 'Todos' },
    { value: 'great-sword', label: 'Grande Espada' },
    { value: 'long-sword', label: 'Espada Longa' },
    { value: 'sword-and-shield', label: 'Espada e Escudo' },
    { value: 'dual-blades', label: 'Lâminas Duplas' },
    { value: 'hammer', label: 'Martelo' },
    { value: 'hunting-horn', label: 'Corneta' },
    { value: 'lance', label: 'Lança' },
    { value: 'gunlance', label: 'Lança de Artilharia' },
    { value: 'switch-axe', label: 'Espadachim' },
    { value: 'charge-blade', label: 'Lâmina Carregada' },
    { value: 'insect-glaive', label: 'Glaive Inseto' },
    { value: 'light-bowgun', label: 'Besta Leve' },
    { value: 'heavy-bowgun', label: 'Besta Pesada' },
    { value: 'bow', label: 'Arco' },
];

const RANK_OPTIONS = [
    { value: '', label: 'Todos' },
    { value: 'MR', label: 'Master Rank' },
    { value: 'HR', label: 'High Rank' },
    { value: 'LR', label: 'Low Rank' },
];

const TIER_COLORS: Record<number, string> = {
    1: '#888', 2: '#4ade80', 3: '#60a5fa', 4: '#fbbf24',
};

const EquipmentPicker: React.FC<EquipmentPickerProps> = ({
    mode, armorType, isOpen, onClose, onSelect
}) => {
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchText, setSearchText] = useState('');
    const [weaponTypeFilter, setWeaponTypeFilter] = useState('');
    const [rankFilter, setRankFilter] = useState('MR');

    // Fetch data when picker opens or filters change
    useEffect(() => {
        if (!isOpen) return;

        const fetchData = async () => {
            setLoading(true);
            try {
                let result;
                if (mode === 'weapon') {
                    result = await getWeapons({
                        type: weaponTypeFilter || undefined,
                        rank: rankFilter || undefined,
                        limit: 200,
                    });
                } else if (mode === 'armor') {
                    result = await getArmor({
                        type: armorType,
                        rank: rankFilter || undefined,
                        limit: 200,
                    });
                } else {
                    result = await getCharms({ limit: 500 });
                }
                setItems(result?.items || []);
            } catch (e) {
                console.error('Failed to load equipment:', e);
                setItems([]);
            }
            setLoading(false);
        };

        fetchData();
    }, [isOpen, mode, armorType, weaponTypeFilter, rankFilter]);

    // Filter by search text (client-side)
    const filtered = useMemo(() => {
        if (!searchText.trim()) return items;
        const lower = searchText.toLowerCase();
        return items.filter((item: any) =>
            (item.name?.toLowerCase().includes(lower)) ||
            (item.name_en?.toLowerCase().includes(lower)) ||
            (item.set_name?.toLowerCase().includes(lower))
        );
    }, [items, searchText]);

    if (!isOpen) return null;

    const title = mode === 'weapon' ? 'Selecionar Arma'
        : mode === 'charm' ? 'Selecionar Amuleto'
            : `Selecionar ${armorType === 'head' ? 'Elmo' : armorType === 'chest' ? 'Peito' : armorType === 'arms' ? 'Braços' : armorType === 'waist' ? 'Cintura' : 'Pernas'}`;

    return (
        <div className="picker-overlay" onClick={onClose}>
            <div className="picker-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="picker-header">
                    <h3 className="picker-title">{title}</h3>
                    <button className="picker-close" onClick={onClose}><X size={18} /></button>
                </div>

                {/* Filters */}
                <div className="picker-filters">
                    <div className="picker-search">
                        <Search size={16} className="picker-search-icon" />
                        <input
                            type="text"
                            value={searchText}
                            onChange={e => setSearchText(e.target.value)}
                            placeholder="Buscar..."
                            className="picker-search-input"
                            autoFocus
                        />
                    </div>

                    <div className="picker-selects">
                        {mode === 'weapon' && (
                            <div className="picker-select-wrapper">
                                <select
                                    value={weaponTypeFilter}
                                    onChange={e => setWeaponTypeFilter(e.target.value)}
                                    className="picker-select"
                                >
                                    {WEAPON_TYPES.map(t => (
                                        <option key={t.value} value={t.value}>{t.label}</option>
                                    ))}
                                </select>
                                <ChevronDown size={14} className="picker-select-icon" />
                            </div>
                        )}

                        {mode !== 'charm' && (
                            <div className="picker-select-wrapper">
                                <select
                                    value={rankFilter}
                                    onChange={e => setRankFilter(e.target.value)}
                                    className="picker-select"
                                >
                                    {RANK_OPTIONS.map(r => (
                                        <option key={r.value} value={r.value}>{r.label}</option>
                                    ))}
                                </select>
                                <ChevronDown size={14} className="picker-select-icon" />
                            </div>
                        )}
                    </div>
                </div>

                {/* List */}
                <div className="picker-list">
                    {loading ? (
                        <div className="picker-loading">
                            <Loader2 size={24} className="animate-spin" />
                            <span>Carregando...</span>
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="picker-empty">Nenhum item encontrado.</div>
                    ) : (
                        filtered.map((item: any) => (
                            <button
                                key={item.id}
                                className="picker-item"
                                onClick={() => { onSelect(item); onClose(); }}
                            >
                                <div className="picker-item__main">
                                    <span className="picker-item__name">{item.name}</span>
                                    {item.name_en && item.name_en !== item.name && (
                                        <span className="picker-item__name-en">{item.name_en}</span>
                                    )}
                                    {item.set_name && (
                                        <span className="picker-item__set">{item.set_name}</span>
                                    )}
                                </div>

                                <div className="picker-item__meta">
                                    {/* Stats for weapons */}
                                    {mode === 'weapon' && (
                                        <>
                                            <span className="picker-item__stat">Atk {item.attack}</span>
                                            <span className={`picker-item__stat ${item.affinity >= 0 ? 'stat-positive' : 'stat-negative'}`}>
                                                {item.affinity >= 0 ? '+' : ''}{item.affinity}%
                                            </span>
                                            {item.element && (
                                                <span className="picker-item__stat stat-element">
                                                    {item.element.type} {item.element.damage}
                                                </span>
                                            )}
                                        </>
                                    )}

                                    {/* Skills for armor/charm */}
                                    {(mode === 'armor' || mode === 'charm') && item.skills && (
                                        <div className="picker-item__skills">
                                            {item.skills.map((s: any, i: number) => (
                                                <span key={i} className="picker-item__skill-tag">
                                                    {s.name} Lv{s.level}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    {/* Slots */}
                                    {item.slots && item.slots.length > 0 && (
                                        <div className="picker-item__slots">
                                            {item.slots.map((tier: number, i: number) => (
                                                <span
                                                    key={i}
                                                    className="picker-item__slot-dot"
                                                    style={{ backgroundColor: TIER_COLORS[tier] || '#555' }}
                                                />
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </button>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default EquipmentPicker;
