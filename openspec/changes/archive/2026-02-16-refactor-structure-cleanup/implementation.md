# Refactor Structure Cleanup

Objective: Remove legacy "backend" and "frontend" directories from root, consolidating into "apps/".

## Actions Taken
- Moved `backend/mhw.db` and `sessions.db` to `apps/backend/src/data/`.
- Moved `backend/splash.html` to `apps/backend/src/templates/`.
- Moved core logic (`mhw_api.py`, `mhw_rag.py`, `game_extractor/`) to `apps/backend/src/core/mhw/`.
- Updated `apps/backend/src/services/monster_service.py` to use new core imports.
- Updated `apps/backend/src/core/mhw/mhw_api.py` to use correct relative DB path.
- Updated `apps/backend/src/core/mhw/mhw_rag.py` to use correct relative data paths.
- Updated `build.py` to build from `apps/backend/src/main.py` and `apps/frontend/`.
- Updated `run.bat` to point directly to `apps/backend/src/main.py`.
- Deleted legacy `backend/` and `frontend/` folders.
- Deleted `update_db.bat` and `extract_game_data.bat` (broken legacy scripts).
- Deleted redundant `game_extractor/` folder in root.

## Verification
- Verified DB connections via script.
- Verified build script configuration.
