# Design: Dados Precisos via Wiki e Tool Calling (LR/HR/MR)

## Contexto
O sistema atual baseia-se em documentos XML extraídos do jogo que são indexados de forma vetorial (RAG). Embora flexível, esse método falha na precisão necessária para builds (slots, níveis exatos de skills e restrições de Rank). O objetivo deste design é migrar a inteligência técnica para um banco de dados SQL extraído da Wiki Fextralife, acessado via Tool Calling.

## Objetivos / Não-Objetivos

### Objetivos:
- Implementar Scrapers eficientes para armaduras/armas da Wiki (LR, HR, MR).
- Estruturar os dados em tabelas SQL otimizadas para busca por Habilidade e Rank.
- Integrar Function Calling (Ferramentas) no fluxo de chat do backend.
- Garantir que o bot use dados reais e verídicos em vez de alucinações estatísticas.

### Não-Objetivos:
- Substituir o RAG para perguntas sobre "Lore", "História" ou "Dicas Gerais" (essas continuam via RAG).
- Criar um sistema de build automático completo em Python (a lógica de combinação ainda fica com a LLM, mas baseada em dados reais).

## Decisões Técnicas

### 1. Sistema de Extração (Scraper)
- **Tecnologia:** `httpx` para requisições assíncronas e `BeautifulSoup4` para parseamento de HTML.
- **Rationale:** Mais rápido e leve que o Playwright/Selenium, dado que as tabelas da Fextralife são servidas via HTML estático.
- **Qualidade:** Implementação de um cache local de páginas HTML para evitar bloqueios de IP e acelerar re-extrações durante testes.

### 2. Arquitetura de Dados (SQL)
- **Tabelas Adicionais no `mhw.db`:**
    - `wiki_armor`: `id`, `name`, `piece_type`, `rank`, `rarity`, `slots` (armazenado como string CSV ou colunas individuais `slot_1`, `slot_2`, `slot_3`), `defense_base`, `defense_max`.
    - `wiki_armor_skills`: `armor_id`, `skill_name`, `level`.
- **Rationale:** O SQL permite fazer JOINs instantâneos. Ex: "Busque todas as peças de MR que dão 'Olho Crítico' e tenham pelo menos 1 slot nível 4". Isso é impossível de fazer com precisão em RAG puro.

### 3. Integração via Tool Calling (Function Calling)
- **Nova Ferramenta Chat:** `search_equipment`.
- **Parâmetros:** `skills` (lista), `rank` (MR/HR/LR), `equipment_type` (armor/weapon).
- **Fluxo:**
    1. A LLM detecta a intenção de build/dados técnicos.
    2. A LLM chama a Tool `search_equipment`.
    3. O backend executa o SQL e retorna um JSON estruturado com as peças exatas.
    4. A LLM recebe o JSON e monta a resposta amigável (Personalidade Gojo).

### 4. Gestão de Performance
- **Inicialização:** Os dados SQL são carregados sob demanda ou cacheados em memória no startup do backend (`main.py`).
- **Latência:** O Tool Calling economiza tokens de contexto do RAG, pois o retorno do SQL é muito mais denso e útil que o conteúdo bruto do XML.

## Riscos / Trade-offs
- **Mudança na Wiki:** Se a Fextralife mudar o layout das tabelas, o scraper precisará de atualização. *Mitigação: Testes de verificação de esquema no scraper.*
- **Complexidade do SQL:** Mapear nomes de skills da Wiki (EN) para o jogo (PT-BR). *Mitigação: Usar os arquivos de texto existentes no database para criar um mapa de tradução robusto.*
