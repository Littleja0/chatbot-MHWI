# Implementation Tasks

## Preparation
- [x] `create-structure`: Create directory hierarchy (`apps/backend`, `apps/frontend`, `tools`, `data`, `src`) <!-- id: 0 -->
- [x] `move-tools`: Move all `hunt_*.py`, `scan_*.py`, `test_*.py`, `dump_*.py` and `build_*.py` to `tools/` <!-- id: 1 -->
- [x] `move-data`: Move `mhw.db`, `.db`, `.html` and `knowledge/` to `data/` <!-- id: 2 -->
- [x] `move-backend`: Move existing `backend` files to `apps/backend/src/legacy` for reference <!-- id: 3 -->
- [x] `move-frontend`: Move existing `frontend` files to `apps/frontend` <!-- id: 4 -->

## Backend Implementation
- [x] `core-module`: Create `apps/backend/src/core/config.py` and `logging.py` <!-- id: 10 -->
- [x] `data-module`: Implement `apps/backend/src/data/db.py` and models <!-- id: 11 -->
- [x] `chat-service`: Implement `apps/backend/src/services/chat_service.py` (logic from old main.py) <!-- id: 12 -->
- [x] `memory-service`: Implement `apps/backend/src/services/memory_service.py` (logic from old memory_reader.py) <!-- id: 13 -->
- [x] `monster-service`: Implement `apps/backend/src/services/monster_service.py` (logic from old mhw_api/rag) <!-- id: 14 -->
- [x] `api-routers`: Create FastAPI routers in `apps/backend/src/api/routers/` <!-- id: 15 -->
- [x] `backend-main`: Create clean entry point `apps/backend/src/main.py` <!-- id: 16 -->

## Frontend Implementation
- [x] `chat-context`: Create `apps/frontend/src/contexts/ChatContext.tsx` <!-- id: 20 -->
- [x] `hooks`: Create `apps/frontend/src/hooks/useChat.ts` and `useMonsterData.ts` <!-- id: 21 -->
- [x] `refactor-app`: Refactor `App.tsx` to use new structure <!-- id: 22 -->
- [x] `update-config`: Update `vite.config.ts` and build scripts <!-- id: 23 -->

## Verification & Cleanup
- [x] `verify-backend`: Test backend build and run <!-- id: 30 -->
- [x] `verify-frontend`: Test frontend build and run <!-- id: 31 -->
- [x] `update-scripts`: Update `run.bat` and `requirements.txt` paths <!-- id: 32 -->
- [x] `cleanup`: Remove duplicate copies from apps/backend/src (kept originals in backend/) <!-- id: 33 -->
