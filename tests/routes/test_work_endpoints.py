"""Integration tests for FastAPI endpoints matching the current API behavior for works."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from music_catalogue.main import app
from music_catalogue.models.exceptions import APIError, ValidationError
from music_catalogue.models.works import Work


class TestWorksEndpoints:
    """Integration tests for works endpoints."""

    def test_get_work_by_id_success(self):
        """GET /works/{id} returns serialized Work when found."""
        client = TestClient(app)
        work = Work(id="work-1", title="Saul og David")

        with patch("music_catalogue.routers.works.works.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = work

            response = client.get("/works/work-1")

            assert response.status_code == 200
            assert response.json() == work.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("work-1")

    def test_get_work_by_id_not_found(self):
        """Uncaught errors propagate as 500 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.works.works.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.side_effect = IndexError()

            response = client.get("/works/missing")

            assert response.status_code == 500

    def test_search_works_success(self):
        """GET /works with valid query returns Work list."""
        client = TestClient(app)
        query = "beethoven"
        works_list = [
            Work(id="work-1", title="Saul og David"),
            Work(id="work-2", title="Maskarade"),
        ]

        with patch("music_catalogue.routers.works.works.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = works_list

            response = client.get("/works", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in works_list]
            mock_search.assert_awaited_once_with(query)

    def test_search_works_requires_query(self):
        """Query parameter is mandatory and validated."""
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/works")

        assert response.status_code == 422

    def test_search_works_query_length_validation(self):
        """Query length is enforced for works search."""
        client = TestClient(app)

        response = client.get("/works", params={"query": "a"})

        assert response.status_code == 422

        response_long = client.get("/works", params={"query": "x" * 51})

        assert response_long.status_code == 422

    def test_create_work_success(self):
        """POST /works returns created work payload."""
        client = TestClient(app)
        payload = {
            "title": "New Work",
        }
        work = Work(id="work-123", title="New Work")

        with patch("music_catalogue.routers.works.works.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = work

            response = client.post("/works", json=payload)

            assert response.status_code == 201
            assert response.json() == work.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()
            forwarded_payload = mock_create.await_args.args[0].model_dump(exclude_none=True)
            assert forwarded_payload == payload

    def test_create_work_validation_error(self):
        """Domain validation errors surface as 400 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.works.works.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValidationError("Invalid")

            response = client.post("/works", json={"title": "Invalid"})

            assert response.status_code == 400
            assert "Invalid" in response.json()["detail"]

    def test_create_work_api_error(self):
        """API errors surface as 500 responses for create."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.works.works.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Upstream failure")

            response = client.post("/works", json={"title": "New Work"})

            assert response.status_code == 500
            assert "Upstream failure" in response.json()["detail"]
