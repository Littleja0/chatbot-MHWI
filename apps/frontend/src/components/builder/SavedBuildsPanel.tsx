import React, { useState } from 'react';
import { useBuildContext } from '../../contexts/BuildContext';
import { useSavedBuilds } from '../../hooks/useSavedBuilds';
import { formatRelativeTime } from '../../utils/buildHelpers';
import './SavedBuildsPanel.css';

export const SavedBuildsPanel: React.FC = () => {
    const { buildState, dispatch } = useBuildContext();
    const { savedBuilds, saveBuild, loadBuild, deleteBuild, renameBuild, isAtLimit } = useSavedBuilds();

    const [isOpen, setIsOpen] = useState(false);
    const [saveName, setSaveName] = useState('');
    const [isSaving, setIsSaving] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editName, setEditName] = useState('');
    const [confirmAction, setConfirmAction] = useState<{ type: 'load' | 'delete'; id: string; name: string } | null>(null);
    const [showFeedback, setShowFeedback] = useState(false);

    const hasEquipment = !!(buildState.weapon || Object.values(buildState.armor).some(a => a !== null));

    const handleSave = () => {
        if (!saveName.trim()) return;
        saveBuild(saveName, buildState);
        setSaveName('');
        setIsSaving(false);
        setShowFeedback(true);
        setTimeout(() => setShowFeedback(false), 2000);
    };

    const handleLoad = (id: string) => {
        const state = loadBuild(id);
        if (state) {
            dispatch({ type: 'LOAD_BUILD', payload: state });
            setConfirmAction(null);
        }
    };

    const handleDelete = (id: string) => {
        deleteBuild(id);
        setConfirmAction(null);
    };

    const handleStartRename = (id: string, currentName: string) => {
        setEditingId(id);
        setEditName(currentName);
    };

    const handleFinishRename = () => {
        if (editingId && editName.trim()) {
            renameBuild(editingId, editName);
        }
        setEditingId(null);
        setEditName('');
    };

    const getWeaponName = (build: typeof savedBuilds[0]) => {
        return build.buildState.weapon?.name || 'Sem arma';
    };

    return (
        <div className="saved-builds-panel">
            <button
                className="saved-builds-panel__toggle"
                onClick={() => setIsOpen(!isOpen)}
            >
                <span className="saved-builds-panel__toggle-icon">{isOpen ? '▼' : '▶'}</span>
                <span>💾 Builds Salvas</span>
                {savedBuilds.length > 0 && (
                    <span className="saved-builds-panel__count">{savedBuilds.length}</span>
                )}
            </button>

            {isOpen && (
                <div className="saved-builds-panel__content">
                    {/* Save Section */}
                    <div className="saved-builds-panel__save-section">
                        {isSaving ? (
                            <div className="saved-builds-panel__save-form">
                                <input
                                    type="text"
                                    className="saved-builds-panel__save-input"
                                    placeholder="Nome da build..."
                                    value={saveName}
                                    onChange={e => setSaveName(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && handleSave()}
                                    autoFocus
                                    maxLength={40}
                                />
                                <button className="saved-builds-panel__btn saved-builds-panel__btn--save" onClick={handleSave} disabled={!saveName.trim()}>
                                    Salvar
                                </button>
                                <button className="saved-builds-panel__btn saved-builds-panel__btn--cancel" onClick={() => setIsSaving(false)}>
                                    ✕
                                </button>
                            </div>
                        ) : (
                            <button
                                className="saved-builds-panel__btn saved-builds-panel__btn--new"
                                onClick={() => setIsSaving(true)}
                                disabled={!hasEquipment || isAtLimit}
                                title={isAtLimit ? 'Limite de 50 builds atingido' : !hasEquipment ? 'Selecione pelo menos uma arma' : 'Salvar build atual'}
                            >
                                ＋ Salvar Build Atual
                            </button>
                        )}
                        {showFeedback && <span className="saved-builds-panel__feedback">✓ Build salva!</span>}
                        {isAtLimit && <span className="saved-builds-panel__limit-msg">Limite de 50 builds atingido. Exclua builds antigas.</span>}
                    </div>

                    {/* Builds List */}
                    {savedBuilds.length === 0 ? (
                        <div className="saved-builds-panel__empty">
                            Nenhuma build salva ainda.
                        </div>
                    ) : (
                        <div className="saved-builds-panel__list">
                            {savedBuilds.map(build => (
                                <div key={build.id} className="saved-builds-panel__item">
                                    <div className="saved-builds-panel__item-info">
                                        {editingId === build.id ? (
                                            <input
                                                type="text"
                                                className="saved-builds-panel__rename-input"
                                                value={editName}
                                                onChange={e => setEditName(e.target.value)}
                                                onBlur={handleFinishRename}
                                                onKeyDown={e => e.key === 'Enter' && handleFinishRename()}
                                                autoFocus
                                                maxLength={40}
                                            />
                                        ) : (
                                            <span
                                                className="saved-builds-panel__item-name"
                                                onClick={() => handleStartRename(build.id, build.name)}
                                                title="Clique para renomear"
                                            >
                                                {build.name}
                                            </span>
                                        )}
                                        <span className="saved-builds-panel__item-meta">
                                            {getWeaponName(build)} · {formatRelativeTime(build.updatedAt)}
                                        </span>
                                    </div>
                                    <div className="saved-builds-panel__item-actions">
                                        <button
                                            className="saved-builds-panel__btn saved-builds-panel__btn--load"
                                            onClick={() => {
                                                if (hasEquipment) {
                                                    setConfirmAction({ type: 'load', id: build.id, name: build.name });
                                                } else {
                                                    handleLoad(build.id);
                                                }
                                            }}
                                            title="Carregar esta build"
                                        >
                                            📂
                                        </button>
                                        <button
                                            className="saved-builds-panel__btn saved-builds-panel__btn--delete"
                                            onClick={() => setConfirmAction({ type: 'delete', id: build.id, name: build.name })}
                                            title="Excluir esta build"
                                        >
                                            🗑
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Confirm Modal */}
                    {confirmAction && (
                        <div className="saved-builds-panel__confirm-overlay">
                            <div className="saved-builds-panel__confirm-modal">
                                <p>
                                    {confirmAction.type === 'load'
                                        ? `Substituir build atual por "${confirmAction.name}"?`
                                        : `Excluir build "${confirmAction.name}"?`}
                                </p>
                                <div className="saved-builds-panel__confirm-actions">
                                    <button
                                        className="saved-builds-panel__btn saved-builds-panel__btn--confirm"
                                        onClick={() =>
                                            confirmAction.type === 'load'
                                                ? handleLoad(confirmAction.id)
                                                : handleDelete(confirmAction.id)
                                        }
                                    >
                                        Confirmar
                                    </button>
                                    <button
                                        className="saved-builds-panel__btn saved-builds-panel__btn--cancel"
                                        onClick={() => setConfirmAction(null)}
                                    >
                                        Cancelar
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
