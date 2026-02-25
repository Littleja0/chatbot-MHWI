import React from 'react';
import { ComputedStats } from '../../types/builder';
import { Swords, Target, Zap, Shield, Flame } from 'lucide-react';
import SkillBar from './SkillBar';
import { SKILL_SECRETS, SKILL_SECRET_MAX_LEVELS } from '../../data/skillSecrets';
import { SKILL_BONUSES } from '../../data/skillBonuses';

interface StatsPanelProps {
    stats: ComputedStats;
}

const StatItem: React.FC<{ icon: React.ReactNode; label: string; value: string | number; color?: string }> = ({
    icon, label, value, color
}) => (
    <div className="stat-item">
        <div className="stat-item__icon" style={{ color: color || '#888' }}>{icon}</div>
        <div className="stat-item__content">
            <span className="stat-item__label">{label}</span>
            <span className="stat-item__value" style={{ color: color || '#fff' }}>{value}</span>
        </div>
    </div>
);

const StatsPanel: React.FC<StatsPanelProps> = ({ stats }) => {
    const affinityColor = stats.affinity >= 0 ? '#4ade80' : '#f87171';
    const efrColor = stats.efr > 500 ? '#fbbf24' : stats.efr > 300 ? '#60a5fa' : '#fff';

    return (
        <div className="stats-panel">
            {/* Combat Stats */}
            <div className="stats-panel__section">
                <h3 className="stats-panel__title">
                    <Swords size={18} />
                    Estatísticas de Combate
                </h3>

                <div className="stats-grid">
                    <div className="stat-item-with-breakdown">
                        <StatItem
                            icon={<Swords size={16} />}
                            label="Ataque (True Raw)"
                            value={stats.trueRaw}
                        />
                        <div className="stat-breakdown">
                            <span className="stat-breakdown__base" title="Base da Arma">{stats.attackBreakdown.base}</span>
                            <span className="stat-breakdown__plus">+</span>
                            <span className="stat-breakdown__skills" title="Bônus de Skills">{stats.attackBreakdown.skills}</span>
                            {stats.attackBreakdown.conditional > 0 && (
                                <>
                                    <span className="stat-breakdown__plus">+</span>
                                    <span className="stat-breakdown__cond" title="Bônus Condicionais (Agitador, etc.)">({stats.attackBreakdown.conditional})</span>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="stat-item-with-breakdown">
                        <StatItem
                            icon={<Target size={16} />}
                            label="Afinidade"
                            value={`${stats.affinity >= 0 ? '+' : ''}${stats.affinity}% `}
                            color={affinityColor}
                        />
                        <div className="stat-breakdown">
                            <span className="stat-breakdown__base" title="Base da Arma">{stats.affinityBreakdown.base}%</span>
                            <span className="stat-breakdown__plus">+</span>
                            <span className="stat-breakdown__skills" title="Bônus de Skills">{stats.affinityBreakdown.skills}%</span>
                            {stats.affinityBreakdown.conditional > 0 && (
                                <>
                                    <span className="stat-breakdown__plus">+</span>
                                    <span className="stat-breakdown__cond" title="Bônus Condicionais (Agitador, WEX, etc.)">({stats.affinityBreakdown.conditional}%)</span>
                                </>
                            )}
                        </div>
                    </div>
                    <StatItem
                        icon={<Zap size={16} />}
                        label="EFR (Dano Efetivo)"
                        value={stats.efr.toFixed(1)}
                        color={efrColor}
                    />
                    {stats.elementDamage > 0 && (
                        <StatItem
                            icon={<Flame size={16} />}
                            label="Elemento"
                            value={stats.elementDamage}
                            color="#c084fc"
                        />
                    )}
                    <StatItem
                        icon={<Shield size={16} />}
                        label="Defesa"
                        value={stats.defense}
                    />
                </div>
            </div>

            {/* Active Skills */}
            <div className="stats-panel__section">
                <h3 className="stats-panel__title">
                    <Zap size={18} />
                    Habilidades Ativas ({stats.activeSkills.length})
                </h3>

                <div className="skills-list">
                    {stats.activeSkills.length === 0 ? (
                        <p className="stats-panel__empty">Equipe armaduras para ver as habilidades.</p>
                    ) : (
                        stats.activeSkills.map((skill) => (
                            <SkillBar key={skill.name} skill={skill} />
                        ))
                    )}
                </div>
            </div>

            {/* Set Bonuses */}
            {stats.activeSetBonuses.length > 0 && (
                <div className="stats-panel__section">
                    <h3 className="stats-panel__title">
                        <Shield size={18} />
                        Bônus de Conjunto
                    </h3>

                    <div className="set-bonus-list">
                        {stats.activeSetBonuses.map((sb) => (
                            <div key={sb.setName} className="set-bonus-card">
                                <div className="set-bonus-card__header">
                                    <span className="set-bonus-card__name">{sb.setName}</span>
                                    <span className="set-bonus-card__count">{sb.piecesEquipped} peças</span>
                                </div>
                                {sb.tiers.map((tier, i) => (
                                    <div
                                        key={i}
                                        className={`set-bonus-card__tier ${tier.active ? 'set-bonus-card__tier--active' : ''}`}
                                    >
                                        <span className="set-bonus-card__pieces">{tier.piecesRequired}p</span>
                                        <span className="set-bonus-card__bonus">{tier.bonus}</span>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default StatsPanel;
