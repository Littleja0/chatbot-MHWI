## Why

Atualmente, o chatbot tem dificuldade em organizar builds e fornecer informações precisas sobre peças de armadura individuais, pois os dados estão agrupados por conjuntos (sets) no RAG. Isso causa confusão entre versões Alfa e Beta e imprecisão na leitura de slots de decoração.

## What Changes

- **Indexação Granular**: Modificação do loader de RAG para criar documentos individuais para cada peça de armadura, além dos documentos de conjunto.
- **Formatação Semântica de Slots**: Tradução de arrays de slots (ex: [4, 1, 0]) para descrições textuais claras (ex: "1 slot de Nível 4, 1 slot de Nível 1").
- **Melhoria no Retrieval**: Ajuste na lógica de expansão de query para priorizar matches específicos de peças e variações (Alfa/Beta).
- **Enriquecimento de Contexto**: Inclusão de tabelas de comparação ou resumos de habilidades de set em cada documento de peça.

## Capabilities

### New Capabilities
- `armor-rag-granularity`: Sistema de recuperação de dados de armaduras com alta precisão e granularidade, distinguindo peças individuais e variações.

### Modified Capabilities

## Impact

- `apps/backend/src/core/mhw/rag_loader.py`: Lógica de carregamento e estruturação dos documentos XML.
- `apps/backend/src/core/mhw/mhw_rag.py`: Lógica de expansão de query e retrieval de contexto.
- `data/storage/`: O índice do LlamaIndex precisará ser reconstruído (automático via hash detection).
