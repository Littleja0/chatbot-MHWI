# RAG Implementation Verification Design

## Context
The application suffered from a "split-brain" data storage issue where configuration pointed to one location (`Root/data`) while legacy code hardcoded paths to another (`apps/backend/src/data`). This caused the RAG system to fail silently or report missing data.

## Goal
Verify and finalize the RAG implementation by enforcing a single, centralized data directory structure and updating all backend services to strictly adhere to the configuration constants.

## Architecture

### 1. Centralized Data Storage
We are adopting a "Root Data" pattern. All persistent state and large assets must reside in `D:/chatbot MHWI/data`.

```
D:/chatbot MHWI/
├── data/
│   ├── rag/           # XML Knowledge Base
│   ├── storage/       # LlamaIndex vector store
│   ├── mhw.db         # Game Data (SQLite)
│   └── sessions.db    # User Chat History (SQLite)
└── apps/backend/src/  # Code only
```

### 2. Configuration-First Access
No module is allowed to guess where data is.
- `core.config.py` is the **only** place where paths are defined.
- All other modules must import:
  ```python
  from core.config import RAG_DIR, STORAGE_DIR, MHW_DB_PATH
  ```

## Implementation Details

### A. Configuration (`core/config.py`)
- Define `DATA_DIR = ROOT_DIR / "data"`
- Define `RAG_DIR` and `STORAGE_DIR` relative to `DATA_DIR`.
- Define database paths as strings or Path objects pointing to `DATA_DIR`.

### B. RAG Core (`mhw_rag.py`, `rag_pipeline.py`)
- Remove local path calculations (e.g., `Path(__file__).parent...`).
- Replace with imports from `core.config`.
- Ensure `rag_pipeline` correctly initializes the index from `STORAGE_DIR`.
- Ensure hot-reloading uses absolute imports (`from core.mhw import mhw_rag`) to avoid module duplication issues.

### C. Database Access (`db.py`, `mhw_api.py`)
- Remove fallback logic that searches for `mhw.db` in multiple locations.
- Hard-bind the connection logic to `MHW_DB_PATH` and `SESSIONS_DB_PATH`.

### D. Data Migration
- A one-time migration is required to move artifacts from `src/data` to `Root/data`.
- This includes moving XMLs and existing `.db` files.
- **Verification**: The system must check for the existence of these files at startup and fail fast (or log a critical error) if missing, rather than silently falling back to defaults.

## Risks / Trade-offs
- **Risk**: Hardcoded paths in other obscure parts of the code.
  - *Mitigation*: Grep search for "data", ".xml", ".db" to ensure all references are caught.
- **Risk**: File permissions when moving databases.
  - *Mitigation*: Ensure the application is stopped before migration.

## Verification Plan
1. **Migration Script**: Run a script to move files.
2. **Debug Script**: Run `debug_rag.py` to confirm paths are resolved correctly and the index can be loaded/generated.
3. **End-to-End**: Start the chat and query for "Tigrex weakness".
