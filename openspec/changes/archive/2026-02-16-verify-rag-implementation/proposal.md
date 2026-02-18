# verify-rag-implementation

## Why
The RAG (Retrieval-Augmented Generation) system was failing to retrieve information because the data directory structure and configuration paths were inconsistent. The application was looking for data in `apps/backend/src/data`, while the configuration pointed to `Root/data`. This caused the chatbot to claim it had no data. To fix this, we need to verify the implementation by centralizing data storage in `Root/data` and updating all code references to use the centralized configuration.

## What Changes
- **Configuration**: Update `apps/backend/src/core/config.py` to point `DATA_DIR`, `RAG_DIR`, `STORAGE_DIR`, `MHW_DB_PATH`, and `SESSIONS_DB_PATH` to `Root/data`.
- **Codebase**: Update `mhw_rag.py`, `rag_loader.py`, `rag_pipeline.py`, `mhw_api.py`, and `db.py` to import paths from `core.config` instead of calculating them relative to `__file__`.
- **Data Migration**: Move all XML files, SQLite databases, and storage directories from `apps/backend/src/data` to `d:\chatbot MHWI\data`.
- **Verification**: Run a debug script to confirm that the RAG pipeline correctly identifies the XMLs and generates embeddings in the new location.

## Capabilities
- `rag-data-centralization`: Centralize all RAG and database files in the root `data/` directory and ensure the backend correctly addresses them via config.

## Impact
- **Backend Core**: Config and RAG modules (`mhw`, `rag_pipeline`, `rag_loader`) will be modified to remove hardcoded relative paths.
- **Data**: The `apps/backend/src/data` folder will be deprecated/removed in favor of `d:\chatbot MHWI\data`.
- **Functionality**: The chatbot will regain access to the knowledge base, enabling it to answer questions about monsters and items.
