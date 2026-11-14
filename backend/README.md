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
- Student profiles, questionnaire sessions, and chatbot/recommendation
  integration are not implemented yet.

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

For protected requests, send:
Authorization: Bearer <access_token>

Access tokens expire after the configured lifetime.
Invalid credentials and disabled accounts are rejected.