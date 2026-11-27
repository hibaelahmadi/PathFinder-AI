# Backend Integration Issues & Dependencies

This file tracks backend dependencies, missing capabilities, and integration blockers encountered while implementing the PathFinder AI frontend. Per team ownership rules, no backend files are modified by the frontend team.

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
