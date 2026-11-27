# Backend Integration Issues & Dependencies

This file tracks backend dependencies, missing capabilities, and integration blockers encountered while implementing the PathFinder AI frontend. Per team ownership rules, no backend files are modified by the frontend team.

## Backend verification update — 2026-11-27

Backend review reproduced successful real HTTP calls on Windows, both directly
at `127.0.0.1:8000` and through the unchanged Vite proxy at
`127.0.0.1:5173/api`: health/docs/OpenAPI, registration/login/current user,
catalogue cards fetched in parallel for comparison, pathways, institutions,
sessions, and sourced evidence. PostgreSQL answered `SELECT 1`; revision
`c4a812f6d930` is applied and `alembic check` reports no drift.

The proxy configuration and the frontend service paths match the current API.
The reported WSL `ECONNREFUSED` is consistent with the missing local backend
environment described in ISSUE-001; successful Windows checks do not establish
that another developer's WSL environment is configured. Its environment setup
remains pending verification by that developer. The exact WSL startup procedure
is now documented in `backend/README.md`, using a separate `.venv-wsl` so an
existing Windows virtual environment is preserved.

Backend diagnostics now include `GET /health/ready` and sanitized JSON 503
responses for unavailable PostgreSQL or missing/outdated schema. The complete
HTTP contract is exported in `backend/openapi.json` for offline inspection.
No frontend source files were changed during this verification.

ISSUE-002 remains unimplemented pending an admin functionality/permissions
contract. ISSUE-003 remains optional: the frontend's existing parallel card
fetches work when the backend is reachable. ISSUE-004 is unchanged: editable
profiles and confirmed questionnaire snapshots remain separate, and Gemini
enrichment is optional. These are not causes of proxy-level HTTP 502 errors.

---

## ISSUE-001: Local backend server not running / environment not configured (HTTP 502 via Vite proxy)

- **Current status:** Open (Blocked on local environment/database setup)
- **Affected endpoints:** All backend endpoints via `/api/*` proxy (including `GET /health`, `POST /auth/login`, `POST /auth/register`, `GET /auth/me`)
- **Expected behavior:** FastAPI listens on `http://127.0.0.1:8000` in WSL Ubuntu so the Vite dev server proxy (`/api` -> `http://127.0.0.1:8000`) forwards frontend requests and returns valid API responses.
- **Actual behavior:** Vite returns `HTTP 502` with `Error: connect ECONNREFUSED 127.0.0.1:8000` because no backend process is running on port `8000`.
- **Reproduction steps:**
  1. Start Vite in WSL (`cd frontend && npm run dev`).
  2. Trigger `POST /api/auth/login` from the frontend UI or `curl http://127.0.0.1:5173/api/auth/login`.
  3. Observe Vite proxy error `ECONNREFUSED 127.0.0.1:8000` and HTTP `502`.
- **Relevant error messages:**
  - `9:32:15 AM [vite] http proxy error: /auth/login`
  - `Error: connect ECONNREFUSED 127.0.0.1:8000`
  - Missing local prerequisites: `backend/.venv` does not exist, `backend/.env` does not exist, and PostgreSQL role `pathfinder_app` / database `pathfinder_db` access is unverified (requires WSL `sudo` / local credentials).
- **Information already sent to the backend developer:** Local startup/env prerequisites documented for WSL Ubuntu (`python3 -m venv .venv`, `pip install -e ".[dev]"`, `alembic upgrade head`, `uvicorn`).

---

## ISSUE-002: No admin-only API endpoints implemented

- **Current status:** Open (Awaiting backend developer decision/implementation)
- **Affected endpoints:** Missing `/admin/*` endpoints (no admin routes exist in `backend/app/api/`)
- **Expected behavior:** For users with `role === "admin"`, dedicated backend endpoints would allow administrative operations (for example: viewing/updating admission verification statuses, managing official sources, or reviewing system catalogue metrics) with server-side `admin` role enforcement.
- **Actual behavior:** `backend/app/schemas/auth.py` and `backend/app/models/user.py` support `role: "student" | "admin"`, and `GET /auth/me` returns the user's `role`, but no router in `backend/app/api/` enforces or exposes admin-specific functionality. Both roles have identical owner-only access to `/profiles/me`, `/sessions/*`, and `/catalogue/evidence`.
- **Reproduction steps:**
  1. Inspect `backend/app/api/*.py` and `backend/app/core/security.py`.
  2. Observe `get_current_user` does not have an admin-role dependency and no `/admin/*` router exists.
- **Relevant error messages:** N/A (feature not implemented in backend).
- **Information already sent to the backend developer:** Pending message to forward to the backend developer (included in final handoff report).

---

## ISSUE-003: No dedicated HTTP comparison endpoint for P4 catalogue cards

- **Current status:** Open (Non-blocking — frontend workaround using existing `GET /catalogue/programs/{program_id}`)
- **Affected endpoints:** Missing `GET /catalogue/compare` (note: `pathfinder_p4.catalog.compare(ids)` exists in Python but is not exposed as a FastAPI route in `backend/app/api/catalogue.py`)
- **Expected behavior:** Optional batch endpoint (e.g., `GET /catalogue/compare?ids=...`) returning multiple P4 program cards in one request.
- **Actual behavior:** Only single-card retrieval `GET /catalogue/programs/{program_id}` is exposed over HTTP.
- **Reproduction steps:** Inspect `backend/app/api/catalogue.py` vs `Pathfinder_P4_Livraison/Pathfinder_P4/src/pathfinder_p4/catalog.py`.
- **Relevant error messages:** N/A (frontend fetches selected program cards in parallel via `GET /catalogue/programs/{program_id}`).
- **Information already sent to the backend developer:** Pending optional enhancement note for the backend developer.

---

## ISSUE-004: Profile vs. questionnaire synchronization and default LLM extraction flag

- **Current status:** Open (Behavioral clarification / non-blocking)
- **Affected endpoints:** `GET /profiles/me`, `PATCH /profiles/me`, `POST /sessions/{session_id}/actions`, `GET /sessions/{session_id}/recommendations`
- **Expected behavior:** Clarify whether edits made in `PATCH /profiles/me` should ever sync into questionnaire recommendations or remain strictly separate, and note that with `QUESTIONNAIRE_ENRICH_PROFILE=false` (the `.env.example` default), `categories_interets`, `categories_competences`, and `code_metier` stay `null` in the questionnaire profile snapshot unless Gemini extraction is enabled.
- **Actual behavior:** Confirmed in `backend/README.md`: `/profiles/me` is intentionally separate from questionnaire session profiles, and `GET /sessions/{session_id}/recommendations` reads only the confirmed questionnaire session snapshot.
- **Reproduction steps:** Inspect `backend/README.md` lines 316-334 and `backend/app/api/recommendations.py`.
- **Relevant error messages:** N/A.
- **Information already sent to the backend developer:** Documented for awareness; frontend clearly communicates to students that recommendations come from their confirmed orientation questionnaire session, while `/profiles/me` stores their editable student profile.
