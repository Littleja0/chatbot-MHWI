# Design: Modular Architecture Refactor

## Background
The current codebase has grown organically, resulting in a monolithic and tightly coupled structure.
This makes maintenance difficult and hinders scalability.
The new architecture aims to separate concerns and improve long-term maintainability.

## Architecture

### Backend Modularization
The backend will be restructured into a layered architecture:

*   **Entry Point**: `apps/backend/src/main.py`
    *   Initializes the application.
    *   Configures logging and environment.
    *   Mounts API routers.
*   **API Layer**: `apps/backend/src/api/`
    *   `routers/`: Defines FastAPI routers for different domains (e.g., `chat.py`, `memory.py`, `monsters.py`).
    *   `models/`: Pydantic models for request/response validation.
*   **Service Layer**: `apps/backend/src/services/`
    *   Core business logic, completely decoupled from HTTP concerns.
    *   `chat_service.py`: Orchestrates chat interactions and RAG.
    *   `memory_service.py`: Handles memory reading/scanning logic.
    *   `monster_service.py`: Managing monster data retrieval.
*   **Data Layer**: `apps/backend/src/data/`
    *   `db.py`: Database connection and session management.
    *   `repositories/`: Data access objects (DAOs) for database interactions.
*   **Core**: `apps/backend/src/core/`
    *   `config.py`: Configuration loading (env vars).
    *   `logging.py`: Logging configuration.

### Frontend Decoupling
The frontend will be refactored to separate UI from logic using React hooks and contexts:

*   **Structure**:
    *   `apps/frontend/src/contexts/`: React Contexts for global state (e.g., `ChatContext`, `AuthContext`).
    *   `apps/frontend/src/hooks/`: Custom hooks for reusable logic (e.g., `useChat`, `useMonsterData`).
    *   `apps/frontend/src/components/`: Pure presentational components.
    *   `apps/frontend/src/services/`: API client services (calls to backend).
    *   `apps/frontend/src/pages/`: Route-level components.

### Tooling Organization
All utility scripts currently in the root will be categorized and moved:

*   `tools/memory_scans/`: Scripts related to memory scanning and pointer hunting (`hunt_*.py`, `scan_*.py`).
*   `tools/data_extraction/`: Scripts for data dumping and building (`dump_*.py`, `build_*.py`).
*   `tools/legacy/`: Old or deprecated scripts.

### Data Management
*   **Database**: The SQLite database (`mhw.db`) will reside in `data/`.
*   **Knowledge Base**: JSON/XML/Text files for RAG will be in `data/knowledge_base/`.

## Data Models
No major schema changes are planned for the database itself, but the access patterns will be formalized through the Repository pattern.

## APIs
The API endpoints will remain largely compatible but organized into routers:
-   `/api/chat`: Chat related endpoints.
-   `/api/memory`: Memory reading endpoints.
-   `/api/monsters`: Monster data endpoints.
-   `/api/user`: User profile endpoints.

## User Interface
The UI will remain visually similar but the underlying code structure will change.
Components will be more focused and reusable.

## Security
-   Environment variables for API keys will be loaded via `core/config.py`.
-   Database file permissions should be restricted.

## Alternatives Considered
-   **Microservices**: Overkill for the current scale and deployment model (local executable).
-   **Monorepo Tools (Nx/Turborepo)**: Added complexity without significant benefit for a single-team project.
