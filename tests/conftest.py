from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from httpx import AsyncClient

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.main import app

# Load environment variables
load_dotenv()

# Configure asyncio mode for pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest_asyncio.fixture
async def supabase_client():
    """Fixture to provide Supabase client for tests."""
    client = await get_supabase()
    yield client


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture to provide async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_client() -> TestClient:
    """Fixture to provide synchronous test client for FastAPI."""
    return TestClient(app)


# Test data fixtures
@pytest.fixture
def sample_uuid() -> str:
    """Sample valid UUID for testing."""
    return "fe9032cc-1b14-402b-b5f5-0151176b1d1c"


@pytest.fixture
def invalid_uuid() -> str:
    """Invalid UUID for error testing."""
    return "not-a-valid-uuid"
