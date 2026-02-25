import React, { useState, useEffect, useMemo } from 'react';
import { Search, X, Loader2, Lock } from 'lucide-react';
import { getDecorations } from '../../services/apiService';

interface DecorationPickerProps {
    isOpen: boolean;
    maxTier: number;       // Maximum tier the slot accepts
    onClose: () => void;
    onSelect: (deco: any) => void;
}

const TIER_COLORS: Record<number, string> = {
    1: '#888', 2: '#4ade80', 3: '#60a5fa', 4: '#fbbf24',
};

const TIER_LABELS: Record<number, string> = {
    1: 'Tier 1', 2: 'Tier 2', 3: 'Tier 3', 4: 'Tier 4',
};

const DecorationPicker: React.FC<DecorationPickerProps> = ({
    isOpen, maxTier, onClose, onSelect
}) => {
    const [allDecos, setAllDecos] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchText, setSearchText] = useState('');

    useEffect(() => {
        if (!isOpen) return;
        if (allDecos.length > 0) return; // Already fetched

        const fetchDecos = async () => {
            setLoading(true);
            try {
                const result = await getDecorations({ limit: 1000 });
                setAllDecos(result?.items || []);
            } catch (e) {
                console.error('Failed to load decorations:', e);
            }
            setLoading(false);
        };

        fetchDecos();
    }, [isOpen, allDecos.length]);

    // Filter and sort
    const { compatible, blocked } = useMemo(() => {
        let decos = allDecos;

        // Text search
        if (searchText.trim()) {
            const lower = searchText.toLowerCase();
            decos = decos.filter(d =>
                d.name?.toLowerCase().includes(lower) ||
                d.skills?.some((s: any) => s.name?.toLowerCase().includes(lower))
            );
        }

        // Split into compatible and blocked
        const comp = decos.filter(d => d.tier <= maxTier);
        const blk = decos.filter(d => d.tier > maxTier);

        return { compatible: comp, blocked: blk };
    }, [allDecos, searchText, maxTier]);

    if (!isOpen) return null;

    return (
        <div className="picker-overlay" onClick={onClose}>
            <div className="picker-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="picker-header">
                    <h3 className="picker-title">
                        Selecionar Joia
                        <span style={{ fontSize: 12, color: '#888', marginLeft: 8 }}>
                            (Slot {TIER_LABELS[maxTier] || `Tier ${maxTier}`})
                        </span>
                    </h3>
                    <button className="picker-close" onClick={onClose}><X size={18} /></button>
                </div>

                {/* Search */}
                <div className="picker-filters">
                    <div className="picker-search">
                        <Search size={16} className="picker-search-icon" />
                        <input
                            type="text"
                            value={searchText}
                            onChange={e => setSearchText(e.target.value)}
                            placeholder="Buscar por joia ou skill..."
                            className="picker-search-input"
                            autoFocus
                        />
                    </div>
                </div>

                {/* List */}
                <div className="picker-list">
                    {loading ? (
                        <div className="picker-loading">
                            <Loader2 size={24} className="animate-spin" />
                            <span>Carregando joias...</span>
                        </div>
                    ) : (
                        <>
                            {/* Compatible decorations */}
                            {compatible.map((deco: any) => (
                                <button
                                    key={deco.id}
                                    className="picker-item"
                                    onClick={() => { onSelect(deco); onClose(); }}
                                >
                                    <div className="picker-item__main">
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            <span
                                                className="deco-slot__diamond"
                                                style={{ backgroundColor: TIER_COLORS[deco.tier] || '#555', width: 10, height: 10 }}
                                            />
                                            <span className="picker-item__name">{deco.name}</span>
                                        </div>
                                        <div className="picker-item__skills" style={{ marginTop: 2 }}>
                                            {deco.skills?.map((s: any, i: number) => (
                                                <span key={i} className="picker-item__skill-tag">
                                                    {s.name} +{s.level}
                                                </span>
                                            ))}
                                        </div>
                                        {deco.skills?.[0]?.description && (
                                            <div className="picker-item__skill-desc">
                                                {deco.skills[0].description}
                                            </div>
                                        )}
                                    </div>
                                    <span className="picker-item__stat" style={{ color: TIER_COLORS[deco.tier] }}>
                                        [{deco.tier}]
                                    </span>
                                </button>
                            ))}

                            {/* Blocked decorations (too high tier) */}
                            {blocked.length > 0 && (
                                <>
                                    <div style={{
                                        padding: '10px 14px 4px',
                                        fontSize: 11,
                                        color: '#555',
                                        textTransform: 'uppercase',
                                        letterSpacing: 1
                                    }}>
                                        Tier incompatível
                                    </div>
                                    {blocked.map((deco: any) => (
                                        <div
                                            key={deco.id}
                                            className="picker-item"
                                            style={{ opacity: 0.35, cursor: 'not-allowed' }}
                                        >
                                            <div className="picker-item__main">
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                    <Lock size={12} style={{ color: '#555' }} />
                                                    <span className="picker-item__name">{deco.name}</span>
                                                </div>
                                            </div>
                                            <span className="picker-item__stat">
                                                [{deco.tier}]
                                            </span>
                                        </div>
                                    ))}
                                </>
                            )}

                            {compatible.length === 0 && blocked.length === 0 && (
                                <div className="picker-empty">Nenhuma joia encontrada.</div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DecorationPicker;
