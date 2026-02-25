import React from 'react';
import { Shield } from 'lucide-react';
import { SetBonus } from '../../types/builder';

interface SetBonusCardProps {
    bonus: SetBonus;
}

const SetBonusCard: React.FC<SetBonusCardProps> = ({ bonus }) => {
    return (
        <div className="set-bonus-card">
            <div className="set-bonus-card__header">
                <span className="set-bonus-card__name">
                    <Shield size={14} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
                    {bonus.setName}
                </span>
                <span className="set-bonus-card__count">
                    {bonus.piecesEquipped} peça{bonus.piecesEquipped !== 1 ? 's' : ''}
                </span>
            </div>

            {bonus.tiers.map((tier, idx) => (
                <div
                    key={idx}
                    className={`set-bonus-card__tier ${tier.active ? 'set-bonus-card__tier--active' : ''}`}
                >
                    <span className="set-bonus-card__pieces">{tier.piecesRequired}p</span>
                    <span className="set-bonus-card__bonus">{tier.bonus}</span>
                </div>
            ))}
        </div>
    );
};

export default SetBonusCard;
