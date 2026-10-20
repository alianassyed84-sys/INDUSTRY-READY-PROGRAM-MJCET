# ReviewPulse backend development (Windows PowerShell)

Milestone 1 is a FastAPI foundation. You do not need PostgreSQL, AI providers, or a frontend to run the API or the automated tests.

Work from PowerShell. Commands below use Windows syntax.

## 1. Verify Python

Prefer Python 3.12 (the project target version) or a supported Python 3.12–3.14 installation:

```powershell
python --version
```

You should see `Python 3.12.x` (or `3.14.x`). If you installed Python 3.12 via `uv`:

```powershell
uv python find 3.12
```

Or check available interpreters via the Python launcher:

```powershell
py -0p
```

## 2. Create a virtual environment

```powershell
cd backend
python -m venv .venv
```

## 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Your prompt should show `(.venv)`.

### If activation is blocked by execution policy

Windows may refuse to run `Activate.ps1` (`PSSecurityException` / execution policy). Do **not** set the machine or user policy to `Unrestricted`.

**Preferred:** skip activation and call the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

**Current session only** (does not change system policy):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Install project dependencies

From `backend/` with the venv active:

```powershell
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Dependencies are declared in `pyproject.toml` (compatible with Python >= 3.12, < 3.15). Exact versions are pinned and verified on Python 3.12.15 and 3.14.3. `uv.lock` records the full cross-version resolved graph. Dependencies can be installed using pip as shown above without secondary requirement files.

Copy the example environment file (it contains no secrets):

```powershell
Copy-Item .env.example .env
```

Edit `.env` locally. Do not commit `.env`.

## 5. Run the FastAPI development server

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The process does not require a live database. `GET /api/v1/ready` will report the database as `unconfigured` until `DATABASE_URL` is set, and will still not report it as healthy until a connectivity check is added.

## 6. Open the API documentation

With the server running, open:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

`GET /api/v1/health` should return HTTP 200.

## 7. Run automated tests

From `backend/`:

```powershell
python -m pytest
```

These tests use FastAPI's test client. They do not connect to production services, AI providers, or a live PostgreSQL instance.

## 8. Run Ruff

```powershell
python -m ruff check .
python -m ruff format --check .
```

To apply formatting:

```powershell
python -m ruff format .
```

## 9. Deactivate the virtual environment

If you used `Activate.ps1`:

```powershell
deactivate
```

## PostgreSQL and Migrations

SQLAlchemy 2.x and Alembic are integrated using the `asyncpg` async driver.

1. If you run a local PostgreSQL instance, verify it with:

```powershell
Get-Service *postgres*
psql --version
```

2. Create an application database and user, then configure `DATABASE_URL` in `backend/.env` (e.g. `postgresql://user:pass@localhost:5432/reviewpulse`).

3. Run migrations:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

4. Check readiness:
- With `DATABASE_URL` unset: `GET /api/v1/ready` returns 503 (`database="unconfigured"`).
- With `DATABASE_URL` set and reachable: `GET /api/v1/ready` returns 200 (`database="ok"`).
- With `DATABASE_URL` set but unreachable: `GET /api/v1/ready` returns 503 (`database="unavailable"`).
