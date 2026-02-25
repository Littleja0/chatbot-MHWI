<artifact id="tasks">
# Lista de Tarefas: Otimização e Qualidade da Engine

## Infraestrutura de Dados
- [x] 1.1 Criar diretório `core/` para lógica central.
- [x] 1.2 Implementar `core/database_manager.py` com conexão persistente ao `mhw.db`.
- [x] 1.3 Criar métodos de busca SQL otimizados para Joias por slot/skill (limite de 5ms).
- [x] 1.4 Adicionar suporte a logging para monitorar performance de queries.

## Modelagem e Abstração
- [x] 2.1 Implementar `core/models.py` usando `dataclasses`.
- [x] 2.2 Definir classes `Equipment`, `Decoration` e `Skill`.
- [x] 2.3 Criar conversores de tuplas SQLite para os modelos de dados.

## Motor de Sugestão (Refatoração)
- [x] 3.1 Criar `core/engine.py` herdando lógica do protótipo mas sem dados hardcoded.
- [x] 3.2 Implementar lógica de 'Scoring' para escolha dinâmica de joias baseada em prioridades.
- [x] 3.3 Adicionar suporte a processamento de slots sem dependência de nomes de peças (lógica genérica).
- [x] 3.4 Validar o novo motor com casos de teste de joias híbridas (Nível 4).

## Limpeza e Promoção
- [x] 4.1 Migrar código final validado e remover `prototype_build_engine.py`.
- [x] 4.2 Deletar arquivos de dump temporários: `model_test_out.txt`, `model_test_out_2.txt`.
- [x] 4.3 Organizar scripts de utilidade: mover `test_naming.py` para diretório `tests/`.
- [x] 4.4 Atualizar `requirements.txt` se novas dependências de performance forem adicionadas.

</artifact>
