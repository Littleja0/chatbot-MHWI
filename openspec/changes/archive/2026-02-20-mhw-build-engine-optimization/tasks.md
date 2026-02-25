# Tasks: MHW Build Engine Optimization

## Task Group: Infraestrutura e Dados
- [x] Criar mapeamento de Joias BiS vs Substitutos no `mhw_tools.py`
- [x] Implementar Helper de consulta ao banco de dados para buscar slots e skills nativas de peças de armadura
- [x] Implementar consulta para Charms (Amuletos) e seus respectivos níveis de skill

## Task Group: Lógica do Build Engine
- [x] Criar função `calculate_build_skills` que soma skills nativas + joias + amuleto
- [x] Implementar lógica de validação de slots (evitar alucinação de encaixe)
- [x] Criar lógica de detecção automática de Set Bonuses baseada no `armorset_id`
- [x] Implementar o motor de sugestão de substitutos para joias de raridade 11 e 12

## Task Group: Integração e Chat
- [x] Registrar a nova ferramenta `validate_build` no metadado `MHW_TOOLS`
- [x] Atualizar o prompt do sistema no `chat_service.py` para obrigar o uso da validação antes da resposta final
- [x] Formatar o output da ferramenta para ser consumido de forma clara pelo LLM (JSON estruturado)

## Task Group: Testes e Refinamento
- [x] Testar cenário de build de "Final Game" (Fatallis/Safi) para garantir bônus complexos
- [x] Validar se as sugestões de substitutos aparecem corretamente no fluxo do Gojo
- [x] Verificar consistência dos nomes PT-BR vs EN nas skills sugeridas
