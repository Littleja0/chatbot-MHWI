import React from 'react';
import { SkillLevel } from '../../types/builder';
import { Lock } from 'lucide-react';

interface SkillBarProps {
    skill: SkillLevel;
}

const SkillBar: React.FC<SkillBarProps> = ({ skill }) => {
    const effectiveMax = skill.isSecretActive ? skill.secretMaxLevel : skill.maxLevel;
    const displayMax = skill.secretMaxLevel > 0 ? skill.secretMaxLevel : (skill.maxLevel > 0 ? skill.maxLevel : skill.currentLevel);
    const totalSegments = displayMax || skill.currentLevel;
    const wasted = effectiveMax > 0 ? Math.max(0, skill.currentLevel - effectiveMax) : 0;
    const filled = effectiveMax > 0 ? Math.min(skill.currentLevel, effectiveMax) : skill.currentLevel;

    return (
        <div className="skill-bar">
            <div className="skill-bar__header">
                <span className="skill-bar__name">{skill.name}</span>
                <span className="skill-bar__level">
                    Lv{skill.currentLevel}
                    {effectiveMax > 0 && `/${effectiveMax}`}
                    {wasted > 0 && <span className="skill-bar__wasted"> (+{wasted})</span>}
                </span>
            </div>
            <div className="skill-bar__segments">
                {Array.from({ length: totalSegments }).map((_, i) => {
                    const segIndex = i + 1;
                    const isFilled = segIndex <= filled;
                    const isSecret = skill.maxLevel > 0 && segIndex > skill.maxLevel;
                    const isWasted = segIndex > effectiveMax && segIndex <= skill.currentLevel;
                    const isLocked = isSecret && !skill.isSecretActive;

                    let className = 'skill-bar__segment';
                    if (isWasted) className += ' skill-bar__segment--wasted';
                    else if (isFilled && isSecret) className += ' skill-bar__segment--secret';
                    else if (isFilled) className += ' skill-bar__segment--filled';
                    else if (isLocked) className += ' skill-bar__segment--locked';

                    return (
                        <div key={i} className={className} title={
                            isLocked ? 'Requer Segredo de Habilidade' :
                                isWasted ? 'Ponto desperdiçado' :
                                    isSecret ? 'Nível Secreto' : undefined
                        }>
                            {isLocked && <Lock size={8} />}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SkillBar;
