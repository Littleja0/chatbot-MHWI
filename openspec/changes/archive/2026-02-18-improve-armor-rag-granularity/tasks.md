## 1. Preparação e Utilitários

- [x] 1.1 Implementar função auxiliar `_format_slots(slots)` no `rag_loader.py` para converter arrays numéricos em descrições textuais (ex: "1 slot de Nível 4").
- [x] 1.2 Implementar lógica de busca de bônus de conjunto por `armorset_id` para injeção em peças individuais no `rag_loader.py`.

## 2. Refatoração do Loader de RAG

- [x] 2.1 Modificar `_load_armor` no `rag_loader.py` para iterar sobre cada peça individual (`armor_id`) e gerar um `Document` separado.
- [x] 2.2 Garantir que o documento de conjunto (set) continue sendo gerado para manter a visão macro.
- [x] 2.3 Aplicar a nova formatação de slots e injeção de bônus de conjunto em ambos os tipos de documentos (peça e set).

## 3. Melhoria na Expansão de Query

- [x] 3.1 Atualizar `_expand_queries` no `mhw_rag.py` para normalizar termos de variações (Alfa/Beta/Gamma e α/β/γ).
- [x] 3.2 Adicionar variações de "b+", "a+", "g+" para garantir o reconhecimento de abreviações comuns de Master Rank.

## 4. Verificação e Rebuild

- [x] 4.1 Disparar o rebuild do índice (via `hot_reload` ou remoção manual da pasta storage) para aplicar as mudanças.
- [x] 4.2 Realizar testes de query: "Slots do Elmo Nargacuga Beta" e verificar se a resposta é precisa e granular.
