import React from 'react';
import SkillBar from './SkillBar';
import { SkillLevel } from '../../types/builder';

interface SkillsSummaryPanelProps {
    skills: SkillLevel[];
}

const SkillsSummaryPanel: React.FC<SkillsSummaryPanelProps> = ({ skills }) => {
    if (skills.length === 0) {
        return <p className="stats-panel__empty">Nenhuma skill ativa. Equipe armadura e joias.</p>;
    }

    // Sort by level descending
    const sorted = [...skills]
        .filter(s => s.currentLevel > 0)
        .sort((a, b) => b.currentLevel - a.currentLevel);

    return (
        <div className="skills-list">
            {sorted.map(skill => (
                <SkillBar
                    key={skill.name}
                    skill={skill}
                />
            ))}
        </div>
    );
};

export default SkillsSummaryPanel;
