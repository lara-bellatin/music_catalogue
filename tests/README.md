# Music Catalogue Testing Framework
This testing framework provides comprehensive coverage for the Music Catalogue API, including unit tests for CRUD operations, integration tests for FastAPI endpoints, and functional tests for search features.

## Test Structure
### 1. **conftest.py** - Test Configuration
Provides pytest fixtures and configuration:
- `supabase_client`: Fixture for Supabase database access
- `async_client`: AsyncClient for testing async endpoints
- `test_client`: Synchronous TestClient for FastAPI
- Sample test data fixtures (IDs, search queries)

### 2. **test_crud.py** - CRUD Unit Tests
Tests for database operations in `music_catalogue.crud`:

#### Search CRUD Tests
- `unified_search`: Search all entities with a single query

#### Works CRUD Tests
- `works.get_by_id`: Retrieve a work with all nested relations
- `works.search`: Search for works by title, identifiers, etc.

#### Artists CRUD Tests
- `test_get_artist_by_id_success`: Retrieve artist with memberships
- `artists.search`: Search for artists and people by legal name, stage name and alternatives

### 3. **test_endpoints.py** - API Integration Tests
Tests FastAPI endpoints with full request/response cycle:

#### Works Endpoints
- `GET /works/{id}`: Retrieve single work
- `GET /works?query=...`: Search works with validation
- Query validation (min 2 chars, max 50 chars)

#### Artists Endpoints
- `GET /artists/{id}`: Retrieve single artist
- `GET /artists?query=...`: Search artists with validation
- Query validation (min 2 chars, max 50 chars)

#### Validation Tests
- Parameter length constraints
- Error handling for invalid input

## Running Tests
### Prerequisites
Install dependencies:
```bash
poetry install
```

### Run All Tests
```bash
poetry run pytest
```

### Run Specific Test File
```bash
poetry run pytest tests/test_crud.py
poetry run pytest tests/test_endpoints.py
```

### Run Tests with Coverage
```bash
poetry run pytest --cov=music_catalogue tests/
```

### Run Only Async Tests
```bash
poetry run pytest -m asyncio
```

### Run with Verbose Output
```bash
poetry run pytest -v
```

## Test Data Requirements
The tests use mocked data and don't require a live database. However, for manual testing with real data:

1. Ensure the Supabase connection is configured in `.env`
2. Populate the database with test data
3. Update the sample UUIDs in `conftest.py` with real IDs from the database
