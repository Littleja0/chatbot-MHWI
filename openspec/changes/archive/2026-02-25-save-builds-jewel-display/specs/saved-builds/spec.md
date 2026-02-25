# Spec: saved-builds

## Overview

Sistema de persistência de builds favoritas no frontend usando localStorage. Permite ao jogador salvar builds que gostou, dar nomes a elas e acessá-las rapidamente para carregamento no Builder.

## ADDED Requirements

### Requirement: Salvar Build Atual

O jogador pode salvar a build atualmente montada no Builder com um nome customizado.

- **GIVEN** o jogador tem pelo menos uma arma selecionada no Builder
- **WHEN** clica em "Salvar Build" e insere um nome (ex: "Meta Longsword Raw")
- **THEN** a build completa (BuildState) é serializada e salva no localStorage com um ID único, nome, e timestamps
- **THEN** um feedback visual confirma que a build foi salva (toast ou highlight)

### Requirement: Listar Builds Salvas

O jogador pode ver todas as builds que salvou previamente.

- **GIVEN** o jogador tem builds salvas no localStorage
- **WHEN** visualiza o painel de builds salvas no Builder
- **THEN** vê uma lista ordenada por data de atualização (mais recente primeiro)
- **THEN** cada item mostra: nome da build, nome da arma, EFR, e data relativa (ex: "há 2 horas")

### Requirement: Carregar Build Salva

O jogador pode restaurar uma build salva previamente.

- **GIVEN** o jogador tem builds salvas e uma build pode estar montada no Builder
- **WHEN** clica em "Carregar" em uma build salva
- **THEN** se a build atual tem equipamentos, exibe confirmação "Substituir build atual?"
- **THEN** ao confirmar, o estado do Builder é substituído pelo estado salvo (dispatch LOAD_BUILD)
- **THEN** todas as peças, jóias, augments e awakenings são restaurados

### Requirement: Excluir Build Salva

O jogador pode remover uma build que não quer mais.

- **GIVEN** o jogador tem builds salvas
- **WHEN** clica em "Excluir" em uma build salva
- **THEN** exibe confirmação "Excluir build 'nome'?"
- **THEN** ao confirmar, a build é removida do localStorage e a lista atualiza

### Requirement: Renomear Build Salva

O jogador pode alterar o nome de uma build salva.

- **GIVEN** o jogador tem builds salvas
- **WHEN** clica no nome da build ou no botão de editar
- **THEN** o campo de nome fica editável (inline edit)
- **THEN** ao confirmar (Enter ou blur), o nome é atualizado no localStorage

### Requirement: Limite de Builds

O sistema limita o número de builds salvas para evitar exceder o localStorage.

- **GIVEN** o jogador tem 50 builds salvas
- **WHEN** tenta salvar uma nova build
- **THEN** exibe mensagem informando que atingiu o limite
- **THEN** sugere excluir builds antigas para liberar espaço

### Requirement: Persistência Entre Sessões

As builds salvas devem sobreviver ao fechamento do navegador.

- **GIVEN** o jogador salvou builds previamente
- **WHEN** fecha o navegador e reabre o app
- **THEN** as builds salvas continuam disponíveis no painel

## Interface Contract

### Hook: useSavedBuilds

```typescript
function useSavedBuilds(): {
    savedBuilds: SavedBuild[];
    saveBuild: (name: string, state: BuildState) => void;
    loadBuild: (id: string) => BuildState;
    deleteBuild: (id: string) => void;
    renameBuild: (id: string, newName: string) => void;
    isAtLimit: boolean;
}
```

### Type: SavedBuild

```typescript
interface SavedBuild {
    id: string;
    name: string;
    createdAt: string;
    updatedAt: string;
    buildState: BuildState;
}
```

### BuildContext Action

```typescript
{ type: 'LOAD_BUILD', payload: BuildState }
```
