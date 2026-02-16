# Proposal: Modular Architecture Refactor

## Problem
The current project structure suffers from significant technical debt:
1.  **Polluted Root Directory**: Over 90 files in the root, mixing production code, experimental scripts, and configuration files.
2.  **Monolithic Backend**: The `backend/main.py` file violates the Single Responsibility Principle, handling API routes, business logic, database initialization, and static file serving all in one place.
3.  **Tightly Coupled Frontend**: The `App.tsx` component is overloaded with logic for state management, API calls, and layout, making it hard to maintain and expand.
4.  **Mixed Concerns**: Data files (`.db`, `.html`) are scattered among code files, and there is no clear distinction between "Application Core" and "Dev Tools".

## Solution
We will refactor the entire project structure into a modular architecture that separates concerns and improves maintainability and performance.
The new structure will strictly separate:
-   **Apps**: Production code for Backend and Frontend.
-   **Tools**: Analysis, debug, and data extraction scripts.
-   **Data**: Database files and heavy assets.

## What Changes
1.  **Directory Structure**: Implement a new root structure with `apps/`, `tools/`, and `data/` directories.
2.  **Backend Refactor**: Decompose `main.py` into a modular `src/` structure with `api/`, `core/`, `services/`, and `data/` modules.
3.  **Frontend Organization**: Move frontend to `apps/frontend` and refactor `App.tsx` to use contexts and hooks, separating logic from UI.
4.  **Root Cleanup**: Move all `scan_*.py`, `hunt_*.py`, and other scripts to a dedicated `tools/` directory.

## Capabilities

### New Capabilities
-   `modular-architecture`: Defines the new project directory structure and module boundaries.
-   `backend-core`: A decoupled backend core that handles configuration and initialization separately from business logic.
-   `frontend-structure`: A clean frontend architecture with separated concerns for components, hooks, and contexts.

### Modified Capabilities
<!-- No existing capabilities to modify yet as we are defining the baseline structure -->

## Impact
-   **Filesystem**: Extensive file moves and renames.
-   **Backend Entry Point**: `backend/main.py` will be replaced by `apps/backend/src/main.py`.
-   **Frontend Entry Point**: `frontend/src/App.tsx` will be refactored.
-   **Scripts**: All root scripts will be moved to `tools/` and may need import updates.
