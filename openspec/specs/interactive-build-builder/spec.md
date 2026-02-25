# Spec: Interactive Build Builder

## Purpose
Define a interface interativa de criação de builds, cálculos de dano e lógica de slots de decoração para fornecer uma ferramenta de "Theorycrafting" robusta integrada ao Chatbot.

## Sub-Capabilities
Esta funcionalidade é composta pelas seguintes especificações detalhadas:
- **[Build Equipment Grid](../build-equipment-grid/spec.md)**: Interface de seleção de peças e joias.
- **[Build Skills Summary](../build-skills-summary/spec.md)**: Painel de habilidades, limites dinâmicos e bônus de set.
- **[Build Stats Engine](../build-stats-engine/spec.md)**: Motor de cálculo de EFR, afinidade e customização de armas.
- **[Build AI Bridge](../build-ai-bridge/spec.md)**: Integração e análise de builds via Chat (Gojo).

## Core Requirements

### Requirement: Tab-Based Navigation
- A aba "Builds" no Header deve ser ativada para trocar a visão principal do Chat para o Builder.
- O estado deve ser preservado ao trocar de abas (não desmontar componentes).

### Requirement: Modular Theorycrafting
O sistema deve permitir que o usuário construa uma build completa do zero ou a partir de uma sugestão do chat, validando slots e calculando o impacto real no dano (EFR).

### Requirement: Visual Feedback
Toda mudança no equipamento ou joias deve resultar em uma atualização instantânea na interface, com feedbacks visuais para skills no nível máximo, secrets desbloqueados e bônus de set ativos.
