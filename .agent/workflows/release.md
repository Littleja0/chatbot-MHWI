---
description: Como lançar uma nova versão do chatbot MHW
---

# 🚀 Fluxo de Release — MHW Chatbot

## Pré-requisitos
- Python 3.12+ com pip
- Node.js/npm instalado
- Acesso à pasta do Google Drive (DRIVE_FOLDER_ID no .env)

---

## Passo a Passo

### 1. Atualizar a versão no `.env`

Abra `.env` e incremente `APP_VERSION`:

```
APP_VERSION=1.0.3   ← nova versão
```

**Regra de versionamento:**
- `1.0.X` → correções de bugs / pequenas melhorias
- `1.X.0` → novas features
- `X.0.0` → mudanças grandes / breaking changes

---

### 2. Rodar o build completo

// turbo
```bash
python build.py
```

Isso executa automaticamente:
1. **Limpeza dos XMLs** (slim_rag_xml)
2. **Instala PyInstaller e dependências**
3. **Build do frontend** (npm install → npm run build)
4. **Build do executável** (PyInstaller → `dist/MHWChatbot/`)
5. **Pré-indexação RAG** (gera a pasta `storage/` para evitar espera do usuário)
6. **Copia assets** (frontend, rag, tools, storage → dist)
7. **Gera o `manifest.json`** dentro de `dist/MHWChatbot/` com todos os hashes SHA256

**Saída final:** `dist/MHWChatbot/` contendo tudo pronto para distribuição.

---

### 3. Upload para o Google Drive

1. Abra a pasta do Google Drive configurada no `.env` (`DRIVE_FOLDER_ID`)
2. **Substitua TODO o conteúdo** da pasta do Drive pelo conteúdo de `dist/MHWChatbot/`
   - Isso inclui: `MHWChatbot.exe`, `frontend/`, `rag/`, `_internal/`, `manifest.json`, etc.
3. **IMPORTANTE:** O arquivo `manifest.json` dentro do Drive DEVE ser o que foi gerado pelo build.
   - Este é o arquivo que o updater baixa para verificar versões e hashes.
   - O `MANIFEST_FILE_ID` no `.env` aponta para este arquivo específico no Drive.

---

### 4. Verificar o ID do manifest.json no Drive

Se você **substituiu** o `manifest.json` (em vez de atualizar o mesmo arquivo):
1. Clique com botão direito no `manifest.json` no Drive → "Obter link"
2. O ID está na URL: `https://drive.google.com/file/d/ESTE_ID_AQUI/view`
3. Atualize `MANIFEST_FILE_ID` no `.env` se o ID mudou

Se você apenas **sobrescreveu** o arquivo existente, o ID permanece o mesmo e não precisa mudar.

---

### 5. Testar o update

Para testar se um usuário receberia a atualização:

```bash
python -c "import updater; updater.update_app()"
```

Deve mostrar:
- `✅ Versão atualizada (1.0.3)` se já está na versão correta
- `✨ Nova versão detectada: 1.0.3` se detectou a atualização

---

## Estrutura dos Arquivos de Release

```
dist/MHWChatbot/
├── MHWChatbot.exe           ← Executável principal
├── manifest.json            ← Manifesto de versão + hashes (auto-gerado)
├── frontend/                ← Build do React/Vite
│   ├── index.html
│   └── assets/
├── rag/                     ← XMLs de dados do jogo
├── storage/                 ← Índice RAG pré-computado
├── game_extractor/tools/    ← Ferramentas de extração
└── _internal/               ← Dependências Python (PyInstaller)
```

## Arquivos Importantes

| Arquivo | Função |
|---|---|
| `.env` → `APP_VERSION` | Define a versão do app |
| `build.py` | Script de build completo |
| `build_manifest.py` | Gera o `manifest.json` com hashes |
| `updater.py` | Verifica e aplica updates via Drive |
| `manifest.json` (Drive) | Fonte de verdade para versão remota |
