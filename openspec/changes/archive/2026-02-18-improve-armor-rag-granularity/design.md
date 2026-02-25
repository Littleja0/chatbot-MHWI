## Context

O sistema de RAG do chatbot MHW:I utiliza o LlamaIndex para indexar dados extraídos de arquivos XML do jogo. Atualmente, a função `_load_armor` no `rag_loader.py` agrupa todas as peças de armadura (Cabeça, Peito, etc.) por `armorset_id`. Isso resulta em documentos extensos que misturam as versões Alfa, Beta e Gamma de um mesmo monstro, dificultando a recuperação de detalhes específicos de uma única peça (como slots e habilidades exatas) pelo LLM.

## Goals / Non-Goals

**Goals:**
- Implementar indexação individual por peça de armadura no `rag_loader.py`.
- Melhorar a legibilidade dos slots de decoração para o LLM.
- Refinar a expansão de consultas para variações de armadura (Alfa/Beta) no `mhw_rag.py`.
- Garantir que cada peça individual mantenha referência ao seu bônus de conjunto.

**Non-Goals:**
- Alterar o esquema dos arquivos XML originais.
- Modificar o sistema de busca de monstros ou armas (nesta fase).
- Implementar um simulador de builds completo (o foco é a qualidade da recuperação dos dados).

## Decisions

### 1. Desregramento da Granularidade de Armaduras
- **Decisão:** Manter o carregamento de conjuntos (sets), mas adicionar um loop secundário para gerar um `Document` para cada `armor_id` individualmente.
- **Racional:** Isso permite que a busca vetorial encontre vizinhos mais próximos extremamente específicos (ex: "Elmo Nargacuga Beta").
- **Alternativa:** Substituir os sets por peças. Rejeitado porque o usuário ainda pode perguntar "Quais as peças do set Nargacuga?", o que exige a visão de conjunto.

### 2. Formatação Textual de Slots
- **Decisão:** Criar uma função auxiliar `_format_slots(slots_list)` que retorna uma string como "1 slot de Nível 4, 1 slot de Nível 1" em vez de `[4, 1, 0]`.
- **Racional:** LLMs interpretam melhor linguagem natural do que representações de arrays compactos, especialmente quando o número '0' pode ser confundido com contagem ou nível.

### 3. Normalização de Termos de Variação (α -> Alfa)
- **Decisão:** No `_expand_queries` do `mhw_rag.py`, injetar termos normalizados. Se a query contém "b+", injetar "Beta", "β" e vice-versa.
- **Racional:** Aumenta o recall independente de como o usuário digita a variação (símbolo grego, letra ou nome por extenso).

### 4. Injeção de Bônus de Set por Peça
- **Decisão:** Ao processar uma peça individual, buscar o `armorset_bonus` associado e incluir uma linha "Habilidade de Conjunto: [Nome]" no texto da peça.
- **Racional:** Permite que o RAG forneça informações sobre bônus de set mesmo quando recupera apenas uma peça isolada.

## Risks / Trade-offs

- **[Risco] Aumento no número de documentos** -> O índice ficará maior. *Mitigação:* As peças individuais são textos curtos; o impacto na memória e latência do LlamaIndex deve ser desprezível dado o volume total de dados do MHW.
- **[Risco] Redundância de informação** -> O nome do set e bônus aparecerão em 5-10 documentos diferentes. *Mitigação:* É uma redundância intencional para garantir que o contexto necessário esteja presente em documentos granulares.
