"""Integration tests for FastAPI endpoints matching the current API behavior for works."""

from unittest.mock import AsyncMock, patch

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.works import Work


class TestWorksEndpoints:
    """Integration tests for works endpoints."""

    def test_get_work_by_id_success(self, test_client):
        """GET /works/{id} returns serialized Work when found."""
        work = Work(id="work-1", title="Saul og David")

        with patch("music_catalogue.routers.works.works.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = work

            response = test_client.get("/works/work-1")

            assert response.status_code == 200
            assert response.json() == work.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("work-1")

    def test_get_work_by_id_not_found(self, test_client):
        """Not found results propagate as 404 responses."""
        with patch("music_catalogue.routers.works.works.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None
            response = test_client.get("/works/missing")
            assert response.status_code == 404

    def test_search_works_success(self, test_client):
        """GET /works with valid query returns Work list."""
        query = "beethoven"
        works_list = [
            Work(id="work-1", title="Saul og David"),
            Work(id="work-2", title="Maskarade"),
        ]

        with patch("music_catalogue.routers.works.works.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = works_list

            response = test_client.get("/works", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in works_list]
            mock_search.assert_awaited_once_with(query)

    def test_search_works_requires_query(self, test_client):
        """Query parameter is mandatory and validated."""
        response = test_client.get("/works")

        assert response.status_code == 422

    def test_search_works_query_length_validation(self, test_client):
        """Query length is enforced for works search."""
        response = test_client.get("/works", params={"query": "a"})

        assert response.status_code == 422

        response_long = test_client.get("/works", params={"query": "x" * 51})

        assert response_long.status_code == 422

    def test_create_work_success(self, test_client):
        """POST /works returns created work payload."""
        payload = {
            "title": "New Work",
        }
        work = Work(id="work-123", title="New Work")

        with patch("music_catalogue.routers.works.works.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = work

            response = test_client.post("/works", json=payload)

            assert response.status_code == 201
            assert response.json() == work.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()

    def test_create_work_validation_error(self, test_client):
        """Domain validation errors surface as 422 responses."""
        with patch("music_catalogue.routers.works.works.create", new_callable=AsyncMock):
            response = test_client.post("/works", json={})

            assert response.status_code == 422

    def test_create_work_api_error(self, test_client):
        """API errors surface as 500 responses for create."""
        with patch("music_catalogue.routers.works.works.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Upstream failure")

            response = test_client.post("/works", json={"title": "New Work"})

            assert response.status_code == 500
            assert "Upstream failure" in response.json()["detail"]
