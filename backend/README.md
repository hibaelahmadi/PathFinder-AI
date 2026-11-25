# PathFinder AI Backend

Backend API built with FastAPI.

## Requirements

- Python 3.12 or newer

## Local configuration

Create a virtual environment and install dependencies as described
in Setup, then copy `.env.example` to `.env` inside `backend`.

Configure your local PostgreSQL credentials in `.env`.

From the backend folder, generate a private token-signing secret:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into `.env`:

```dotenv
JWT_SECRET_KEY="your_generated_secret"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Keep the generated secret private. Never commit `.env`.
The placeholder in `.env.example` must be replaced locally.

Database migration commands also load these settings, so configure
the signing secret before running Alembic.

## Setup

From the project root, enter the backend folder:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Install the backend and its dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

## Run locally

From the backend folder:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- Health endpoint: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs

Press Ctrl+C in the terminal to stop the server.

## Current functionality

- GET /health checks that the API responds.
- PostgreSQL tables are managed through Alembic migrations.
- Catalogue list and detail endpoints cover institutions, campuses,
  programs, careers, admission criteria, and official sources.
- Catalogue lists support pagination and resource-specific filters.
- Registration, login, and current-user endpoints are implemented and manually verified.
- Student profile creation, reading, and partial updates are implemented
  with access restricted to the authenticated owner.
- Questionnaire session creation and owner-protected reading are implemented.
- Questionnaire answers, corrections, confirmation, and reopening are connected
  to Person 3's questionnaire module.
- Owner-protected recommendations use a confirmed questionnaire profile,
  Person 5's engine, and Person 4's exploration catalogue.
- P4 catalogue cards, sources, vocabulary, and authenticated evidence retrieval
  are available through the same FastAPI application.
- Browser access is restricted to the origins configured in `CORS_ORIGINS`.

## Run tests

From the backend folder, install the development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run the tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Database setup

Install PostgreSQL and create a login role named `pathfinder_app`
with a private password.

Create a database named `pathfinder_db` owned by `pathfinder_app`.

Copy `.env.example` to `.env` and set your local database credentials.
Never commit `.env`.

From the backend folder, apply the existing migrations:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Check the applied revision:

```powershell
.\.venv\Scripts\python.exe -m alembic current
```

Check whether the database matches the models:

```powershell
.\.venv\Scripts\python.exe -m alembic check
```

## PostgreSQL tests

Create a separate database named `pathfinder_test_db`, owned by
`pathfinder_app`. Tests use the connection credentials from `.env`
but explicitly select this test database.

Apply the migrations to the test database from PowerShell:

```powershell
$previousDbName = $env:DB_NAME
try {
    $env:DB_NAME = "pathfinder_test_db"
    .\.venv\Scripts\python.exe -m alembic upgrade head
}
finally {
    if ($null -eq $previousDbName) {
        Remove-Item Env:DB_NAME -ErrorAction SilentlyContinue
    }
    else {
        $env:DB_NAME = $previousDbName
    }
}
```

Run the database tests:

```powershell
$env:RUN_DB_TESTS = "1"
try {
    .\.venv\Scripts\python.exe -m pytest tests/test_catalogue_database.py -v
}
finally {
    Remove-Item Env:RUN_DB_TESTS -ErrorAction SilentlyContinue
}
```

Database tests are skipped unless `RUN_DB_TESTS=1`.
Each test rolls back its changes; sequence counters may still advance.

## Catalogue API

Each resource supports GET listing and lookup by numeric ID:

| Resource | List endpoint | Optional filters |
|---|---|---|
| Institutions | /institutions | None |
| Campuses | /campuses | institution_id |
| Programs | /programs | campus_id, institution_id, field |
| Careers | /careers | program_id |
| Admission criteria | /admission-criteria | program_id, academic_year, campaign, verification_status |
| Sources | /sources | program_id, criterion_id |

All lists accept offset (default 0) and limit (default 20, maximum 100).
Filters combine with AND. Empty results return [].
Missing individual records return 404; invalid parameters return 422.

Annual tuition is expressed in MAD and serialized as a decimal string.
Unknown values are returned as null.

Program source filtering returns direct program-source links;
admission evidence is retrieved using criterion_id.

## Authentication API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/register | Create a student account |
| POST | /auth/login | Return a bearer access token |
| GET | /auth/me | Return the authenticated account |

Registration and login accept JSON containing email and password.
Passwords must contain 15–128 characters. Email addresses are
normalized to lowercase.

Registration does not accept a role; new accounts are students.
Responses never include password hashes.
The database supports `student` and `admin` roles. Both use the same owner-only
profile/session rules; registration cannot grant administrative privileges.

For protected requests, send:
Authorization: Bearer <access_token>

Access tokens expire after the configured lifetime.
Invalid credentials and disabled accounts are rejected.

## Student profiles

Authentication is required.

- GET /profiles/me returns the logged-in account's profile.
  Returns 404 if no profile exists.
- PATCH /profiles/me creates or partially updates that profile.

Omitted fields remain unchanged. Explicit null clears a field.
Lists and grades dictionaries are replaced rather than merged.

Grades must be between 0 and 20. Annual budgets are nonnegative
amounts in MAD. Clients cannot supply user_id.

Profile creation, partial updates, validation, and isolation between
two accounts were manually verified through the local API.

## Questionnaire sessions

Authentication is required.

- POST /sessions starts an in-progress questionnaire and returns its first
  expected question code.
- GET /sessions lists the authenticated user's sessions.
- GET /sessions/{session_id} retrieves an owned session.
- GET /sessions/{session_id}/answers lists its saved answers.
- GET /sessions/{session_id}/state returns the saved questionnaire state,
  next question, profile snapshot, and confirmation flag for resuming a session.
- POST /sessions/{session_id}/actions processes a questionnaire action.

List endpoints support offset and limit.
Other users' sessions return 404; unauthenticated requests return 401.

Session creation, retrieval, ownership isolation, and pagination
validation were verified through the local API.

After pulling these changes, reinstall from the backend folder:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

This installs both the backend and `ai.chatbot` from the repository, allowing
the usual backend-folder launch command to import the questionnaire module.

Example action body:

```json
{
  "action": "answer",
  "reponse": {
    "question_code": "bac",
    "answer_text": "Sciences mathématiques"
  }
}
```

Supported actions are `start`, `answer`, `correct`, `confirm`, and `reopen`.
Only `answer` and `correct` accept a `reponse`; both require it.
Optional `question_text` and `answer_value` metadata are accepted, but the
questionnaire module recalculates them from the original answer text.
Blank answers are supported where the module permits skipping a question.
Mobility accepts `oui`, `non`, or `je ne sais pas`.

The last answer leaves the session in progress until an explicit `confirm`.
Reopening clears confirmation, keeps answers, and requires a new confirmation.
Corrections can remove obsolete dependent answers. Successful actions save
answer changes and session state atomically. Session row locks serialize
simultaneous actions. Validation errors return 422 and leave stored data intact.

The returned result follows the module contract, including `etat`,
`next_question`, answer changes, `profile`, `profile_confirmed`, and `errors`.
The session profile contains the module's original fields, including
`competences_declarees` and boolean `confirme`. Confirmation validates the
summary and does not guarantee all recommendation inputs are available.

New sessions use Person 3's questionnaire at commit `4233f57`. They collect:

- `notes`: an object mapping subject identifiers to numeric grades from 0 to 20,
  or `null`. Subjects without a grade are omitted.
- `budget_annuel_max`: a nonnegative number or `null`, representing annual tuition
  in MAD, excluding registration fees, housing, and transport.
- `type_etablissement`: `"public"`, `"prive"`, or `null` for no preference or unknown.
- `code_bac`: the recognized Sciences mathématiques A/B code, or `null` when
  uncertain. The original `bac` text is preserved; ambiguous A/B adds a
  `precision_bac` question.

The questionnaire module validates these values; the backend preserves their
JSON types in JSONB. Original textual answers remain saved separately.
After the original questions, budget and type are asked, then optional grades
using `note:<subject_code>`. Empty grade answers skip that subject; zero remains
a real grade. Read the next question from `/sessions/{session_id}/state` or the
last action result rather than hardcoding the order.

Each session saves its question options, ordered subject codes, allowed
categories, and next question. This keeps settings stable across server restarts
and preserves the exact question during resume. The codes come from P4's
versioned draft-1 vocabulary; they are not validated admission criteria.
Older sessions retain their original options and remain readable. Start a new
session to use the full new questionnaire. The migration adding this context
is `c4a812f6d930`; apply it with `alembic upgrade head` before running the API.

The normalized `/profiles/me` record is a separate optional editable profile.
Recommendations use the confirmed session snapshot through P5's adapter,
so the backend does not copy it into that separate profile automatically.

Gemini enrichment of interest/skill/career codes is optional. Install its
dependencies from `backend` with:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,gemini]"
```

P3's module reads `GEMINI_API_KEY` from the repository-root `.env` (not
`backend/.env`). Keep that private file ignored. To enable enrichment, set
`QUESTIONNAIRE_ENRICH_PROFILE=true` in `backend/.env` and restart the API.
It is disabled by default. A valid confirmation can call Gemini up to three
times; unavailable or uncertain extraction leaves the corresponding category
null, while original answers remain saved. Read-only resume does not call the
LLM or overwrite the saved enriched profile. Live Gemini calls require P3's
configuration; backend integration was verified with mocked extraction.

The connected flow was verified against `pathfinder_test_db`, including
skipped answers, confirmation, reopening, dependency deletion, ownership,
validation rollback, simulated persistence failure, and simultaneous actions.

## Recommendations

`GET /sessions/{session_id}/recommendations?top_n=5` uses the authenticated
owner's saved profile. It returns 401 without authentication, 404 for a missing
or another user's session, and 409 until the session and its profile are
confirmed. Reopening a questionnaire blocks recommendations until reconfirmed.
`top_n` accepts 1 to 100; invalid values return 422.

The response contains `recommendations` and `location_to_verify`, with a total
candidate count for each. When mobility is refused, formations in the requested
city appear in `recommendations`; formations without a usable location appear
separately in `location_to_verify`. Each list returns up to `top_n` results.
With no preferred city, or mobility allowed or undecided, `recommendations`
contains the engine's overall ranking and `location_to_verify` is empty.
Nullable city and constraint reasons still identify unknown locations.

Scores, explanations, and location grouping come from Person 5's
`recommend_grouped()` at commit `0721f0e`, with integration documentation from
`d7a5baa` (PR #10).
Missing inputs are allowed; scores can be null and unknown admission, cost,
or location information remains explicitly flagged. The unresolved comparison
between Person 3's 12 and Person 5's 11 matching-city formations is not treated
as a validated agreement.

The backend validates profile types, finite grades/budget, and vocabulary codes
before passing the saved questionnaire profile to P5's adapter. An invalid
saved profile returns 409 and must be corrected. No structured interest/skill
category is inferred by the backend from free text. This
adapter uses `code_bac` for eligibility and preserves `bac` separately as
`bac_text`. A missing or ambiguous bac code stays unknown; the backend does not
infer a code from the text. Harmonizing the subject/category vocabulary remains
a team integration task.

P4's delivery in `Pathfinder_P4_Livraison/Pathfinder_P4` was retrieved from
`main` commit `b9db7a74d8d2c467e1321459140677427c450eae`, with its source code,
data, retrieval index, provenance, and documentation preserved.
Recommendations use `institutions.json` and `programs_exploration.json`
(87 formations). This endpoint
reads that snapshot directly; it does not import it into PostgreSQL. P4 string
identifiers remain strings and must not be used as numeric catalogue API IDs.
Source references, catalogue status, provisional matching status, and notes are
returned alongside each result. Exploration results do not establish current
admission availability. A missing or unreadable catalogue returns 503.

Local API checks against the test database reproduced P5's 46 retained
formations (11 matching Rabat, 35 with location to verify), checked ranking
parity, authentication, ownership, confirmation/reopening, zero budget, empty
results, and unavailable catalogue handling. Test records were rolled back.

Reinstall the editable backend after pulling to include `ai.recommendation`:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Run Person 5's catalogue demo from the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m ai.recommendation.demo_catalogue
```

To try the authenticated API from `/docs`, register or log in, authorize with
the returned bearer token, complete and confirm a questionnaire session, then
call `GET /sessions/{session_id}/recommendations?top_n=5` with its numeric ID.
The saved profile is used; a caller cannot submit another profile in this GET.

Run P5's regression tests from the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m unittest discover -s ai/recommendation -p "test_*.py" -v
```

## P4 catalogue and sourced retrieval

P1 should use these routes for the delivered dataset. P4 IDs are strings, and
the numeric PostgreSQL catalogue routes above remain a separate API.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /catalogue/programs | Explore programs, with optional history |
| GET | /catalogue/programs/{program_id} | Program card, institution, sources and warnings |
| GET | /catalogue/institutions | Institutions |
| GET | /catalogue/careers | Career records |
| GET | /catalogue/sources | Source registry |
| GET | /catalogue/pathways | P4's general pathway records |
| GET | /catalogue/vocabulary/current | Draft subject, bac and matching codes |
| POST | /catalogue/evidence | Authenticated sourced retrieval |

Lists return `total` and `items`; `offset` defaults to 0 and `limit` to 20
(maximum 100). Programs accept `city`, `sector`, `field`, `direct_post_bac`,
and `include_archive` (false by default). These are P4's catalogue filters;
the stricter location handling for recommendations is provided by P5.
Missing program cards return 404; invalid inputs return 422.

Evidence requests require a bearer token and accept:

```json
{
  "query": "ENSA Marrakech cycle preparatoire",
  "filters": {"institution_id": "PUB056"},
  "top_k": 3
}
```

Allowed filters: `institution_id`, `program_id`, `city`, `sector`, `field`,
`academic_year`, `direct_post_bac`, `exploration_visible`, `source_id`.
Values may be single values or lists; boolean filters require JSON booleans.
`top_k` is an integer from 1 to 50. Use `exploration_visible=true` when
retrieving evidence for suggestions; historical evidence retains its year.

Responses contain `status` (`ok` or `no_evidence`), `evidence`, and
`admission_verified=false`. Each passage preserves P4's text, content type,
source ID, official URL, document title/publisher, location within the source,
documentary year, check date, verification status, and retrieval score.
No retrieved evidence means no supporting passage was found. Retrieval scores
are distinct from student compatibility scores and admission probabilities.
An unavailable or stale index returns 503. The supplied TF-IDF/LSA index is
local and requires no API key. Rebuilding or ingesting data remains P4's workflow.

The delivery's checksums depend on exact bytes. `.gitattributes` disables
line-ending conversion for this delivery so its index remains usable after clone.
The backend install includes the P4 package and its NumPy/SciPy runtime needs.
P4's broader offline ingestion/index-building commands have their own optional
dependencies and instructions in the delivery README.

## Frontend handoff and final verification

The API runs at `http://127.0.0.1:8000`. Set `CORS_ORIGINS` in `backend/.env`
to a JSON array of P1's browser origins, including protocol and port. The
defaults are `http://localhost:3000` and `http://localhost:5173`. Send access
tokens using the Authorization header; this configuration does not use cookies.

Use `/docs` or `/openapi.json` for request/response formats. A frontend flow is:

1. Register/login, then authorize with the returned bearer token.
2. Create a session and load its state.
3. Submit the displayed question's code and original text with action `answer`.
4. At the summary, explicitly `confirm`; retrieve the session recommendations.
5. Read each P4 card using its string program ID and show its source warnings.
6. For corrections, `reopen`, submit `correct`, answer dependent questions,
   and confirm again. Recommendations return 409 during correction.

Local checks exercised this full flow against the separate test database,
including optional extraction with mocked responses, saved-question resume,
validation and persistence rollback, legacy sessions, and actual sourced
retrieval. Temporary test records were rolled back. No live LLM calls were made.
The schema was checked with Alembic in both local databases.

Run the existing module suites from the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s ai/chatbot -p "test*.py" -q
.\backend\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s ai/recommendation -p "test_*.py" -q
.\backend\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s Pathfinder_P4_Livraison/Pathfinder_P4/tests -p "test*.py" -q
```

UTF-8 mode avoids a Windows encoding mismatch in P4's temporary HTML test fixture.
Backend pytest and PostgreSQL test instructions are above. P1's actual UI flow,
live Gemini behavior, and recommendation relevance still need the team review
before release; these are separate from the verified local backend handoff.
