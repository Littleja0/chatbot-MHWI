# Proposta: Remoção do Leitor de Memória para Máxima Performance

## Problema
O sistema atual utiliza o `memory_reader.py` (via Pymem) para ler dados em tempo real do MHW. Embora potente, isso traz:
- Sobrecarga de CPU/RAM desnecessária para usuários que buscam apenas consulta.
- Dependência de permissões de Administrador.
- Fragilidade contra atualizações do jogo (offsets morrem).
- Código complexo e difícil de manter no `main.py`.

## Solução
Remover completamente a infraestrutura de leitura de memória e transicionar para um modelo **Pure RAG + Manual Profiling**.

## Impacto
- **Performance**: Inicialização instantânea, zero overhead de scan de processo.
- **Segurança**: Não requer privilégios elevados.
- **Funcionalidade**: Perda do overlay de dano em tempo real e sincronização automática de Rank. Isso será substituído por atualização manual de perfil via chat/interface.

## Capabilities
- **pure-rag-consultation**: O sistema deve operar sem qualquer acesso à memória ou processos externos, garantindo 100% de estabilidade e performance.
- **manual-profile-management**: O usuário assume o controle total do MR/HR e inventário de joias através da interface de perfil ou comandos de chat.

## User Review Requerida
Sim, o usuário confirmou que deseja remover a leitura de memória.
