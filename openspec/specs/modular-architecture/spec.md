# Specs: Modular Architecture Refactor

## New Capabilities

### `modular-architecture`
<!-- Defines the core structure of the application -->

-   **Structure Definition**
    -   MUST implement the directory layout:
        -   `apps/backend/src/` for backend source code.
        -   `apps/frontend/src/` for frontend source code.
        -   `tools/` for utility scripts.
        -   `data/` for database and persistent storage.
    -   MUST move `backend/main.py` functionality to `apps/backend/src/api/routers/` and `apps/backend/src/services/`.
    -   MUST refactor `frontend/src/App.tsx` logic into `apps/frontend/src/contexts/` and `apps/frontend/src/hooks/`.

### `backend-core`
<!-- Defines the core infrastructure of the backend -->

-   **Configuration**
    -   MUST load environment variables centrally in `apps/backend/src/core/config.py`.
    -   MUST initialize logging in `apps/backend/src/core/logging.py`.
-   **Service Layer**
    -   MUST decouple business logic from API handlers.
    -   MUST contain `chat_service.py` for chat logic.
    -   MUST contain `memory_service.py` for memory reading logic.

### `frontend-structure`
<!-- Defines the structure of the frontend application -->

-   **Component Architecture**
    -   MUST use React Context for global state (Chat, Auth).
    -   MUST extract data fetching logic into custom hooks.
    -   MUST separate presentation components from business logic.

## Modified Capabilities

<!-- None: This is a foundational change establishing new capabilities. -->
