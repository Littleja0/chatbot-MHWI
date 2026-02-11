# Chatbot Monster Hunter World Specialist

Este projeto é um assistente virtual especializado em Monster Hunter World e Iceborne, capaz de fornecer informações detalhadas sobre builds, monstros, e itens, utilizando dados extraídos diretamente do jogo.

## Funcionalidades
- **Chat Interativo**: Interface moderna com tema Monster Hunter.
- **Base de Dados Local**: Utiliza dados extraídos diretamente do jogo (mhw.db).
- **Extração Automática**: Ferramenta para extrair dados atualizados dos arquivos do jogo.
- **Busca Especializada**: Consulta dados precisos de fraquezas, hitzones e drops.
- **Geração de Builds**: Sugere builds otimizadas com base nas informações do jogo.
- **Estratégias de Combate**: Dicas de como enfrentar monstros.

## Como Executar

### Pré-requisitos
1. **Python 3.8+** instalado. Certifique-se de marcar a opção "Add Python to PATH" durante a instalação.
2. Uma chave de API da NVIDIA (já configurada no código).

### Passo a Passo
1. Abra o arquivo `run.bat` (duplo clique).
2. O script instalará as dependências automaticamente e iniciará o servidor.
3. Acesse o chatbot em seu navegador: `http://localhost:8000`

## 🔄 Atualizar Dados do Jogo

Para extrair dados diretamente da sua instalação do MHW:Iceborne:

```bash
cd backend
python extract_game_data.py
```

O script irá:
1. Localizar automaticamente o MHW via Steam
2. Extrair dados dos arquivos chunk
3. Gerar um banco de dados SQLite atualizado

Para mais detalhes, veja [game_extractor/README.md](backend/game_extractor/README.md).

### Estrutura do Projeto
```
├── backend/
│   ├── main.py                 # Servidor FastAPI
│   ├── mhw_api.py             # API de dados do jogo
│   ├── mhw.db                 # Banco de dados SQLite
│   ├── download_db.py         # Baixa DB do GitHub
│   ├── extract_game_data.py   # Extrai dados do jogo
│   └── game_extractor/        # Módulo de extração
│       ├── game_finder.py     # Localiza instalação MHW
│       ├── chunk_extractor.py # Extrai chunks
│       ├── data_parser.py     # Parseia dados
│       └── db_builder.py      # Constrói banco SQLite
├── frontend/                   # Interface web
└── requirements.txt           # Dependências Python
```

## Tecnologias
- Python (FastAPI)
- SQLite (banco de dados local do jogo)
- HTML5, CSS3, JavaScript (Vanilla)
- API NVIDIA (Moonshot AI Kimi-k2.5)
- DuckDuckGo Search (para busca de informações em tempo real)

