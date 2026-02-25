import React from 'react';
import { SkillLevel } from '../../types/builder';
import { Lock } from 'lucide-react';

interface SkillBarProps {
    skill: SkillLevel;
}

const SkillBar: React.FC<SkillBarProps> = ({ skill }) => {
    const effectiveMax = skill.isSecretActive && skill.secretMaxLevel > 0
        ? skill.secretMaxLevel
        : (skill.maxLevel > 0 ? skill.maxLevel : 0);
    const displayMax = skill.secretMaxLevel > 0 ? skill.secretMaxLevel : (skill.maxLevel > 0 ? skill.maxLevel : skill.currentLevel);
    const totalSegments = displayMax || skill.currentLevel;
    const wasted = effectiveMax > 0 ? Math.max(0, skill.currentLevel - effectiveMax) : 0;
    const filled = effectiveMax > 0 ? Math.min(skill.currentLevel, effectiveMax) : skill.currentLevel;
    const isCapped = effectiveMax > 0 && skill.currentLevel === effectiveMax;
    const isOvercapped = wasted > 0;

    return (
        <div className="skill-bar">
            <div className="skill-bar__header">
                <span className={`skill-bar__name ${isCapped ? 'skill-bar__name--capped' : ''} ${isOvercapped ? 'skill-bar__name--overcapped' : ''}`}>
                    {skill.name}
                </span>
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
                    const isWastedSeg = segIndex > effectiveMax && segIndex <= skill.currentLevel;
                    const isLocked = isSecret && !skill.isSecretActive;
                    const isCapSegment = isCapped && isFilled;

                    let className = 'skill-bar__segment';
                    if (isWastedSeg) className += ' skill-bar__segment--wasted';
                    else if (isCapSegment) className += ' skill-bar__segment--capped';
                    else if (isFilled && isSecret) className += ' skill-bar__segment--secret';
                    else if (isFilled) className += ' skill-bar__segment--filled';
                    else if (isLocked) className += ' skill-bar__segment--locked';

                    return (
                        <div key={i} className={className} title={
                            isLocked ? 'Requer Segredo de Habilidade' :
                                isWastedSeg ? 'Ponto desperdiçado' :
                                    isSecret ? 'Nível Secreto' :
                                        isCapSegment ? 'Nível máximo atingido' : undefined
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
