# Spec: Backend Core

## Capabilities

### `manual-profile-management`
<!-- Manages user profile data without reliance on memory reading -->

- **Manual Profile Updates**
    - MR (Master Rank) and HR (Hunter Rank) MUST be read exclusively from `sessions.db`.
    - Use MR from database to filter equipment in build lookups (NO live memory reading).

- **No Auto-Sync**
    - MUST REMOVE "Auto-sync" or "Memory Connect" UI/logic.
    - `/user/profile` MUST return only persisted data.

### `pure-rag-consultation`
<!-- Enforces RAG-only consultation without game memory context -->

- **Disable Memory Reader**
    - System MUST NOT import or initialize `memory_reader.py`.
    - No Memory Scan attempts allowed.
    - Server startup log MUST show only FastAPI and RAG engine init.

- **RAG-Only Chat**
    - Context for LLM MUST contain ONLY data from XMLs via RAG and persisted profile.
    - Answers about monsters MUST use XML data, NOT live game status (HP, etc.).
