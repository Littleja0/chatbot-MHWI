import React, { useState } from 'react';
import { Send, RotateCcw, MessageSquare, X } from 'lucide-react';
import { useBuildContext } from '../../contexts/BuildContext';
import { useChatContext } from '../../contexts/ChatContext';
import { buildToReadableText } from '../../utils/buildSerializer';

const BuildExporter: React.FC = () => {
    const { buildState, computedStats, dispatch } = useBuildContext();
    const { handleSendMessage } = useChatContext();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [customMessage, setCustomMessage] = useState('Analise essa build. Como posso melhorar o dano sem perder sobrevivência?');

    const hasWeapon = buildState.weapon !== null;

    const handleExport = () => {
        if (!hasWeapon) return;
        setIsModalOpen(true);
    };

    const confirmExport = () => {
        const buildText = buildToReadableText(buildState, computedStats);
        const finalMessage = `${buildText}\n\n---\n${customMessage}`;

        handleSendMessage(finalMessage);
        setIsModalOpen(false);

        // Switch to chat tab
        window.dispatchEvent(new CustomEvent('switch-tab', { detail: 'chat' }));
    };

    const handleReset = () => {
        if (window.confirm('Tem certeza que deseja limpar toda a build?')) {
            dispatch({ type: 'RESET_BUILD' });
        }
    };

    return (
        <>
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

            {isModalOpen && (
                <div className="picker-overlay" onClick={() => setIsModalOpen(false)}>
                    <div className="prompt-modal" onClick={e => e.stopPropagation()}>
                        <div className="picker-header">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <MessageSquare size={18} color="#3b82f6" />
                                <h3 className="picker-title">Análise do Gojo</h3>
                            </div>
                            <button className="picker-close" onClick={() => setIsModalOpen(false)}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="prompt-modal__body">
                            <label className="prompt-modal__label">O que você quer que o Gojo analise?</label>
                            <textarea
                                className="prompt-modal__textarea"
                                value={customMessage}
                                onChange={(e) => setCustomMessage(e.target.value)}
                                placeholder="Ex: Analise essa build. O que posso trocar para ter mais afinidade?"
                                autoFocus
                            />
                        </div>

                        <div className="prompt-modal__footer">
                            <button
                                className="build-exporter__btn"
                                style={{ flex: 'none', padding: '8px 20px' }}
                                onClick={() => setIsModalOpen(false)}
                            >
                                Cancelar
                            </button>
                            <button
                                className="build-exporter__btn build-exporter__btn--primary"
                                style={{ flex: 'none', padding: '8px 24px' }}
                                onClick={confirmExport}
                            >
                                <Send size={16} />
                                Enviar Build
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default BuildExporter;
