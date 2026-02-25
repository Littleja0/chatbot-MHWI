<artifact id="design">
## Contexto
O projeto atual possui uma engine de builds (`prototype_build_engine.py`) que utiliza estruturas de dados estáticas (dicionários) para representar armas, armaduras e joias. Além disso, a lógica de sugestão de joias é baseada em ramificações `if-else` rígidas. Existe um banco de dados SQLite completo (`mhw.db`), mas ele é pouco explorado.

## Objetivos
1.  **Arquitetura em Camadas**: Separar a lógica de acesso a dados da lógica de negócio (sugestão de builds).
2.  **Singleton/Pool de Conexão**: Implementar uma forma eficiente de consultar o banco de dados sem abrir/fechar conexões repetidamente.
3.  **Abstração de Modelos**: Criar classes/estruturas que representem as entidades do jogo (Armor, Decoration, Weapon) para garantir tipagem e clareza.

## Abordagem Técnica
### 1. Camada de Dados (`database_manager.py`)
Criar um gerenciador central para o `mhw.db`. 
- Uso de `sqlite3`.
- Métodos otimizados para buscar decorações por nível de slot e tipo de skill.
- SQL queries indexadas para garantir performance < 10ms.

### 2. Refatoração da Engine (`core/build_engine.py`)
Mover a lógica do protótipo para um módulo core.
- A engine não conterá dados. Ela receberá um objeto `BuildData` e consultará o `DatabaseManager` para preencher os slots.
- Implementação de um sistema de "Ranking" simples para sugestão de joias (ex: Priorizar joias com raridade maior ou skills específicas solicitadas pelo usuário).

### 3. Limpeza de Arquivos
Remover scripts de teste antigos e arquivos de saída temporários para manter o ambiente de trabalho limpo e profissional.

## Riscos / Trade-offs
- **Dependência de SQLite**: Toda a lógica passará a depender da integridade do arquivo `.db`.
- **Complexidade Inicial**: A transição de dicionários para classes aumenta o número de arquivos, mas melhora a manutenção a longo prazo.
</artifact>
