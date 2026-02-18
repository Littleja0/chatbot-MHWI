# RAG Data Centralization Spec

This specification defines the requirements for centralizing the Retrieval-Augmented Generation (RAG) data and SQLite databases into a single, canonical location: the project root's `data/` directory.

## Background
Previously, data was scattered between `apps/backend/src/data` (legacy location) and the root `data/` folder (intended new location). Inconsistent configuration and relative path imports caused the backend to fail in locating RAG XML files and the vector store, leading to "no data found" errors during chat interactions.

## Requirements

### 1. Centralized Data Directory
The system **MUST** use `d:\chatbot MHWI\data` as the single source of truth for all persisted data.

- **Storage Structure**:
  - `data/rag/`: Must contain all source XML source files (monsters, items, etc.).
  - `data/storage/`: Must contain the generated vector store indices and RAG manifest.
  - `data/mhw.db`: Must be the active SQLite database for game data.
  - `data/sessions.db`: Must be the active SQLite database for chat history.

- **Acceptance Criteria**:
  - `os.path.exists("data/rag")` returns True.
  - `os.path.exists("data/storage")` returns True.
  - `os.path.exists("data/mhw.db")` returns True.

### 2. Configuration-Driven Paths
All Python modules accessing data files **MUST** import path constants from `core.config`.

- **Constants**:
  - `DATA_DIR`: Root data path.
  - `RAG_DIR`: Path to XML files.
  - `STORAGE_DIR`: Path to vector store.
  - `MHW_DB_PATH`: Absolute path to `mhw.db`.
  - `SESSIONS_DB_PATH`: Absolute path to `sessions.db`.

- **Forbidden Patterns**:
  - No module shall calculate data paths using `__file__` (e.g., `Path(__file__).parent...`).
  - No fallback logic to legacy directories.

### 3. RAG Initialization & Indexing
The RAG pipeline **MUST** correctly initialize from the new location.

- **Behavior**:
  - On startup, check `DATA_DIR/storage`.
  - If valid index exists, load it.
  - If missing or outdated (XMLs changed), rebuild index from `DATA_DIR/rag`.
  
- **Acceptance Criteria**:
  - Calling `mhw_rag.get_rag_response("tigrex")` returns context derived from `monster.xml` located in `data/rag`.

### 4. Database Connectivity
The application handlers for SQLite **MUST** connect to the databases in the centralized location.

- **Acceptance Criteria**:
  - `mhw_api.py` query functions return data from `data/mhw.db`.
  - `db.py` session functions read/write to `data/sessions.db`.

## Migrations needed
- Move all contents from `apps/backend/src/data` to `data/`.
- Delete `apps/backend/src/data` to prevent confusion.
