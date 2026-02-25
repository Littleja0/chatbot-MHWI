# Spec: Build Validation Capacity

## Overview
Esta especificação define como o sistema deve validar uma build completa de Monster Hunter World Iceborne, garantindo que as peças de armadura, o amuleto e as joias sugeridas sejam tecnicamente possíveis e matematicamente precisas de acordo com os dados do jogo.

## Requirements

### Requirement: Validação de Slots de Joias
- **AS A** Sistema de Build
- **I WANT TO** Verificar se o nível de cada joia é menor ou igual ao nível do slot disponível na peça de armadura ou arma.
- **THEN** Impedir que o chatbot sugira joias nível 2 em slots nível 1, por exemplo.

### Requirement: Somatória de Habilidades (Skills)
- **AS A** Assistente Especialista
- **I WANT TO** Somar os pontos de habilidade de três fontes: Peças de Armadura (Innatas), Amuleto e Joias encaixadas.
- **THEN** Apresentar o nível total final da habilidade ao usuário, respeitando o limite máximo (CAP) definido no `mhw.db`.

### Requirement: Bônus de Conjunto (Set Bonuses)
- **AS A** Especialista Supremo
- **I WANT TO** Detectar quando o número mínimo de peças de um mesmo conjunto (ex: 3 peças de Teostra) é atingido.
- **THEN** Ativar e listar o bônus de conjunto resultante na build final.

### Requirement: Integração com Amuleto (Charm)
- **AS A** Engenheiro de Builds
- **I WANT TO** Permitir a inclusão de um Amuleto como peça obrigatória da build.
- **THEN** Adicionar os pontos de habilidade do amuleto ao cálculo total.

## User Scenarios

### Scenario: Validação de Slot Incorreto
- **GIVEN** Uma peça de armadura com apenas um slot nível 1.
- **WHEN** O LLM tentar sugerir uma `Attack Jewel+ 4`.
- **THEN** O sistema deve invalidar a sugestão ou forçar a substituição por uma `Attack Jewel 1`.

### Scenario: Ativação de Master's Touch
- **GIVEN** Uma build com Elmo, Peito e Braços de Teostra (Kaiser Set).
- **WHEN** O sistema processar as peças.
- **THEN** Deve indicar que o bônus "Teostra Technique (Master's Touch)" está ATIVO.
