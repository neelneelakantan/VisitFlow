

\# \*\*Architecture Overview\*\*



VisitFlow is designed as a lightweight, human‑centered workflow engine that supports intentional job‑search habits, cognitive unloading, and structured follow‑ups. The architecture emphasizes clarity, separation of concerns, and future extensibility without unnecessary complexity.



This document describes the system’s structure, routing model, data flow, and design principles.



\---



\# \*\*1. High‑Level Design Goals\*\*



VisitFlow is intentionally:



\- \*\*Simple\*\* — minimal dependencies, JSON durability for MVP.

\- \*\*Predictable\*\* — no hidden state, no silent overrides.

\- \*\*Human‑centered\*\* — supports human speed, focus, and emotional stability.

\- \*\*Extensible\*\* — clean layering allows future SQLite/Postgres, browser extensions, agents, or NLP search.

\- \*\*Maintainable\*\* — clear boundaries between API, UI, and storage.



The system is built to evolve without architectural debt.



\---



\# \*\*2. Layered Architecture\*\*



VisitFlow uses a clean, acyclic dependency structure:



```

main.py

&#x20;  ↓

routes\_api.py      routes\_pages.py

&#x20;  ↓                     ↓

store.py            store.py

&#x20;  ↓                     ↓

JSON files         templates/

```



Each layer has a single responsibility.



\---



\# \*\*3. Application Layer (`main.py`)\*\*



`main.py` is the top‑level orchestrator.



\### Responsibilities

\- Create the FastAPI application.

\- Include the API router and UI router.

\- Provide a simple root/health endpoint.

\- Define global middleware (if needed later).



\### Rules

\- Routers import store, but store never imports routers.

\- `main.py` sits at the top of the dependency graph.



\---



\# \*\*4. API Layer (`routes\_api.py`)\*\*



The API router exposes \*\*JSON endpoints\*\* for programmatic access.



\### Responsibilities

\- CRUD operations for companies.

\- Visit and apply actions.

\- Overdue logic.

\- NLP pipeline endpoint (`/visit`).

\- FreeNotes API (`/api/freenotes`).



\### Rules

\- Only `/api/...` or `/companies/...` routes.

\- Must not render templates.

\- Must not import `routes\_pages`.

\- Must not hold in‑memory state.

\- Must call into `store.py` for persistence.



This keeps the API clean, testable, and future‑proof for CLI, mobile, or agent integrations.



\---



\# \*\*5. UI Layer (`routes\_pages.py`)\*\*



The UI router renders HTML templates for human interaction.



\### Responsibilities

\- Dashboard and company list.

\- Company detail and edit pages.

\- FreeNotes list and creation pages.

\- Timeline, explorer, and other UI views.



\### Rules

\- Only non‑API routes (`/`, `/companies`, `/freenotes`, etc.).

\- Must not import `routes\_api`.

\- Must not duplicate API routes.

\- Must call into `store.py` for persistence.



This separation keeps UI logic clean and prevents circular imports.



\---



\# \*\*6. Store Layer (`store.py`)\*\*



The store module is the \*\*single source of truth\*\* for persistence and business logic.



\### Responsibilities

\- Load and save JSON data.

\- Manage FreeNotes (ID generation, timestamps).

\- Manage Company storage.

\- Provide reusable functions for both routers.



\### Rules

\- Must not import any router.

\- Must not render templates.

\- Must not depend on FastAPI.



This makes it easy to migrate from JSON → SQLite → Postgres without touching routers.



\---



\# \*\*7. Data Durability\*\*



\### MVP (1.0)

\- JSON files stored locally.

\- Simple, portable, no external dependencies.

\- Easy to inspect and debug.



\### Future (2.0)

\- SQLite for indexing, search, pagination.

\- SQL injection protections.

\- Migrations and schema evolution.



\### Long‑term (3.0+)

\- Cloud storage or encrypted local DB.

\- Background agents for job‑site scanning.

\- NLP‑powered search across notes and companies.



\---



\# \*\*8. Routing Model\*\*



\### API Routes (JSON)

\- `/companies`

\- `/companies/{id}`

\- `/companies/{id}/visit`

\- `/companies/{id}/apply`

\- `/companies/overdue`

\- `/api/freenotes`

\- `/visit` (pipeline)

\- `/api/visits`

\- `/api/visit/{id}`



\### UI Routes (HTML)

\- `/`

\- `/companies`

\- `/companies/new`

\- `/companies/{id}`

\- `/freenotes`

\- `/freenotes/new`

\- `/timeline`

\- `/api-explorer`



This separation prevents silent overrides and keeps the system predictable.



\---



\# \*\*9. Design Principles\*\*



\### \*\*1. No global state\*\*

All data is loaded fresh from disk on each request.



\### \*\*2. No circular imports\*\*

Routers never import each other.  

Store never imports routers.



\### \*\*3. Clear separation of concerns\*\*

API = JSON  

UI = HTML  

Store = persistence  

Pipeline = NLP transformation



\### \*\*4. Human‑centered workflow\*\*

The system supports:

\- intentionality  

\- focus  

\- emotional stability  

\- cognitive unloading  



\### \*\*5. Future‑proofing\*\*

The architecture is designed to evolve without rewrites.



\---



\# \*\*10. Future Enhancements\*\*



\- Pagination and search.

\- FreeNotes detail view.

\- Tagging and NLP search.

\- SQLite migration.

\- Authentication (local or Windows).

\- Browser extension.

\- Background agents for job‑site scanning.

\- Analytics and insights.



\---



\# \*\*Conclusion\*\*



This architecture keeps VisitFlow small, clean, and powerful.  

It supports your workflow today while leaving room for future evolution — without architectural debt or complexity.



\---



