# Tasks

## 1. Environment & Configuration
- [x] 1.1 Verify `d:\chatbot MHWI\data` directory structure exists (rag, storage). <!-- id: verify-data-dir -->
- [x] 1.2 Verify `apps/backend/src/core/config.py` defines `DATA_DIR` as `ROOT_DIR / "data"` and uses it for all sub-paths. <!-- id: verify-config -->

## 2. Codebase Standardization
- [x] 2.1 Verify `apps/backend/src/core/mhw/mhw_rag.py` imports paths from `core.config`. <!-- id: verify-mhw-rag -->
- [x] 2.2 Verify `apps/backend/src/core/mhw/rag_pipeline.py` imports paths from `core.config`. <!-- id: verify-rag-pipeline -->
- [x] 2.3 Verify `apps/backend/src/core/mhw/rag_loader.py` imports paths from `core.config`. <!-- id: verify-rag-loader -->
- [x] 2.4 Verify `apps/backend/src/core/mhw/mhw_api.py` imports `MHW_DB_PATH` from `core.config`. <!-- id: verify-mhw-api -->
- [x] 2.5 Verify `apps/backend/src/data/db.py` imports DB paths from `core.config`. <!-- id: verify-db-module -->

## 3. Data Migration & Validation
- [x] 3.1 Confirm RAG XML files are present in `d:\chatbot MHWI\data\rag`. <!-- id: check-xmls -->
- [x] 3.2 Confirm `mhw.db` and `sessions.db` are present in `d:\chatbot MHWI\data`. <!-- id: check-dbs -->
- [x] 3.3 Validate RAG functionality using a test script (e.g. `debug_rag.py`) to ensure embeddings can be generated/loaded. <!-- id: run-verification -->
