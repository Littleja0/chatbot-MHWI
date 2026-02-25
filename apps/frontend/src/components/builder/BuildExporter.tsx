import React from 'react';
import { Send, RotateCcw } from 'lucide-react';
import { useBuildContext } from '../../contexts/BuildContext';
import { useChatContext } from '../../contexts/ChatContext';
import { buildToReadableText } from '../../utils/buildSerializer';

const BuildExporter: React.FC = () => {
    const { buildState, computedStats, dispatch } = useBuildContext();
    const { handleSendMessage } = useChatContext();

    const hasWeapon = buildState.weapon !== null;

    const handleExport = () => {
        if (!hasWeapon) return;

        const text = buildToReadableText(buildState, computedStats);
        handleSendMessage(text);

        // Switch to chat tab (if parent controls tabs)
        // We dispatch a custom event that App.tsx can listen for
        window.dispatchEvent(new CustomEvent('switch-tab', { detail: 'chat' }));
    };

    const handleReset = () => {
        if (window.confirm('Tem certeza que deseja limpar toda a build?')) {
            dispatch({ type: 'RESET_BUILD' });
        }
    };

    return (
        <div className="build-exporter">
            <button
                className="build-exporter__btn"
                onClick={handleReset}
                title="Limpar build"
            >
                <RotateCcw size={16} />
                Limpar
            </button>
            <button
                className="build-exporter__btn build-exporter__btn--primary"
                onClick={handleExport}
                disabled={!hasWeapon}
                title={hasWeapon ? 'Enviar build para o Gojo analisar' : 'Selecione ao menos uma arma'}
            >
                <Send size={16} />
                Enviar para Gojo
            </button>
        </div>
    );
};

export default BuildExporter;
