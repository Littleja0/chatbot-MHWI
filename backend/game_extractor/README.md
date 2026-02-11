# 🎮 Extrator de Dados do Monster Hunter World: Iceborne

Este módulo permite extrair dados diretamente dos arquivos do jogo MHW:Iceborne instalado no seu computador, garantindo informações 100% atualizadas.

## 📋 Requisitos

1. **Monster Hunter World: Iceborne** instalado via Steam
2. **Python 3.8+** 
3. **Ferramenta de extração** (uma das opções abaixo):
   - [WorldChunkTool](https://github.com/mhvuze/WorldChunkTool/releases)
   - [MHWNoChunk](https://www.nexusmods.com/monsterhunterworld/mods/411)

## 🚀 Como Usar

### Método 1: Execução Automática

```bash
cd backend
python extract_game_data.py
```

O script irá:
1. Localizar automaticamente sua instalação do MHW via Steam
2. Extrair os arquivos necessários (requer ferramenta)
3. Parsear os dados do jogo
4. Gerar um banco de dados SQLite atualizado

### Método 2: Caminho Manual

Se o jogo não for encontrado automaticamente:

```bash
python extract_game_data.py --path "D:/SteamLibrary/steamapps/common/Monster Hunter World"
```

### Método 3: Apenas Testar Localização

```bash
python -m game_extractor.game_finder
```

## 📁 Estrutura do Projeto

```
game_extractor/
├── __init__.py          # Módulo principal
├── game_finder.py       # Localiza instalação do MHW
├── chunk_extractor.py   # Extrai arquivos dos chunks
├── data_parser.py       # Parseia dados do jogo
├── db_builder.py        # Constrói banco SQLite
├── tools/               # Coloque WorldChunkTool.exe aqui
└── extracted_data/      # Dados extraídos (gerado)
```

## ⚙️ Opções de Linha de Comando

| Opção | Descrição |
|-------|-----------|
| `--path`, `-p` | Caminho para instalação do MHW |
| `--output`, `-o` | Nome do banco de dados de saída (padrão: mhw.db) |
| `--skip-extract` | Pular extração e usar dados já extraídos |
| `--merge` | Mesclar com banco de dados existente |

## 📊 Dados Extraídos

O sistema extrai as seguintes informações:

### Monstros
- Nomes (múltiplos idiomas)
- Fraquezas elementais (estrelas)
- Fraquezas a status
- Hitzones (valores de dano por parte do corpo)
- Recompensas por rank (LR/HR/MR)
- Eficácia de armadilhas

### Itens
- Nomes e descrições
- Raridade
- Preços de compra/venda
- Limite de transporte

## 🔧 Configuração da Ferramenta de Extração

1. Baixe [WorldChunkTool](https://github.com/mhvuze/WorldChunkTool/releases) ou [MHWNoChunk](https://www.nexusmods.com/monsterhunterworld/mods/411)

2. Extraia o executável para `backend/game_extractor/tools/`

3. A DLL `oo2core_8_win64.dll` é necessária e será copiada automaticamente da pasta do jogo

## ⚠️ Notas Importantes

- **Espaço em disco**: A extração completa requer ~10-20GB de espaço temporário
- **Tempo**: O processo pode demorar 15-30 minutos dependendo do sistema
- **Iceborne**: O sistema detecta automaticamente se Iceborne está instalado
- **Backup**: Um backup do banco de dados existente é criado automaticamente

## 🔄 Atualização de Dados

Para atualizar os dados após uma atualização do jogo:

```bash
python extract_game_data.py --merge
```

Isso irá extrair novos dados e mesclar com o banco existente, mantendo informações que não foram alteradas.

## 🐛 Solução de Problemas

### "MHW não encontrado"
- Verifique se o jogo está instalado via Steam
- Use `--path` para especificar o caminho manualmente

### "Ferramenta de extração não encontrada"
- Baixe WorldChunkTool ou MHWNoChunk
- Coloque o .exe em `backend/game_extractor/tools/`

### "Erro ao extrair chunk"
- Verifique se o jogo não está em execução
- Certifique-se de que há espaço em disco suficiente
- Verifique se a DLL oo2core está presente

## 📝 Licença

Os dados extraídos são propriedade da Capcom. Este projeto é apenas para uso pessoal/educacional.
