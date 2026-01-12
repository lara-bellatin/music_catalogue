# Music Catalogue API

Music Catalogue is a FastAPI service that exposes REST endpoints for exploring classical and popular music metadata stored in Supabase. The project bundles domain models for different musical entities such as works, artists, people, genres, etc. plus CRUD utilities and a unified search RPC for full-text discovery across entities.

## Features
- Async FastAPI application with automatic OpenAPI documentation at `/docs`.
- Supabase-backed CRUD modules for all entities, including deep relational selects.
- Unified search endpoint that allows users to query from all entities.
- Pydantic models describing works, artists, releases, versions, and supporting entities.
- Pytest suite validating CRUD behavior, endpoint contracts, and helper utilities.

## Project Structure
```
music_catalogue/
├── music_catalogue/
│   ├── crud/             # Supabase access helpers for entities and general search
│   ├── models/           # Pydantic domain models and parsing utilities
│   └── main.py           # FastAPI application wiring endpoints to CRUD layer
├── supabase/             # Local Supabase configuration and SQL migrations
├── tests/                # Pytest suites for CRUD modules and API routes
├── pyproject.toml        # Poetry configuration and dependency definitions
└── README.md
```

## Prerequisites
- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation)
- Supabase project credentials (`SUPABASE_URL` and `SUPABASE_KEY`)
- Optional: Supabase CLI for running migrations locally (`npm install -g supabase`)

## Local Setup
1. Install dependencies:
	```bash
	poetry install
	```
2. Create a `.env` file at the project root with your Supabase credentials:
	```env
	SUPABASE_URL="https://your-project.supabase.co"
	SUPABASE_KEY="your-service-role-key"
	```
3. (Optional) Start Supabase locally and apply migrations:
	```bash
	supabase start
	supabase db reset
	```

## Running the API
```bash
poetry run uvicorn music_catalogue.main:app --reload
```

- Interactive Swagger UI: http://127.0.0.1:8000/docs
- ReDoc UI: http://127.0.0.1:8000/redoc

## Key API Endpoints

| Method | Path            | Description                                 |
|--------|-----------------|---------------------------------------------|
| GET    | `/search`       | Unified search across all entities          |
| GET    | `/works/{id}`   | Fetch a work by internal identifier         |
| GET    | `/works`        | Search works by text query                  |
| GET    | `/artists/{id}` | Fetch an artist by internal identifier      |
| GET    | `/artists`      | Search artists and people by text query     |

Query parameters are validated using FastAPI `Query` definitions (e.g., `min_length=2`, `max_length=50`, `limit` range `1-100`).

## Testing and Quality Gates
Run the full test suite:
```bash
poetry run pytest
```

Run a subset (e.g., CRUD tests):
```bash
poetry run pytest tests/crud
```

Optional coverage report:
```bash
poetry run pytest --cov=music_catalogue
```

Static analysis with Ruff:
```bash
poetry run ruff check .
```
