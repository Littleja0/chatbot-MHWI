# Tarefas: Dados Precisos via Wiki e Tool Calling (LR/HR/MR)

Implementação da extração de dados da Wiki e integração de Tool Calling no chatbot.

## 1. Extração de Dados (Wiki Scraper)
- [x] 1.1 Criar o script `tools/data_extraction/wiki_scraper.py` usando `httpx` e `BeautifulSoup4`.
- [x] 1.2 Implementar lógica de cache local para evitar requisições repetidas à Wiki.
- [x] 1.3 Desenvolver extratores para Tabelas de Armadura (LR, HR e MR).
- [x] 1.4 Desenvolver extratores para Tabelas de Armas (todas as categorias e ranks).
- [x] 1.5 Validar a extração de Slots (garantindo que [4, 2, 1] seja capturado corretamente).

## 2. Banco de Dados (SQL)
- [x] 2.1 Criar script de migração para adicionar as tabelas `wiki_armor` e `wiki_armor_skills` ao `mhw.db`.
- [x] 2.2 Popular o banco de dados com os dados extraídos da Wiki.
- [x] 2.3 Criar índices nas colunas de `skill_name` e `rank` para performance.

## 3. Backend e Tool Calling
- [x] 3.1 Implementar a função `search_equipment` no backend para realizar buscas SQL complexas.
- [x] 3.2 Registrar a nova ferramenta (Tool) na configuração da LLM em `apps/backend/src/services/chat_service.py`.
- [x] 3.3 Atualizar a lógica do `process_chat` para gerenciar o fluxo de chamada de função (Function Calling).

## 4. Prompt e Perfil
- [x] 4.1 Atualizar o `system_instruction` para instruir a LLM a usar a ferramenta de busca sempre que dados técnicos de build forem solicitados.
- [x] 4.2 Integrar o Rank do usuário (`user_mr`) e Inventário de Joias (`user_jewels`) como filtros automáticos na chamada da ferramenta.

## 5. Verificação e Testes
- [x] 5.1 Testar build de Master Rank (ex: Teostra/Velkhana) e conferir slots com a Wiki.
- [x] 5.2 Testar build de Low Rank para garantir que o bot não sugira itens de RM.
- [x] 5.3 Validar se a personalidade do Gojo continua intacta após a integração técnica.
