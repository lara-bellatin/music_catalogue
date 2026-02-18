"""Integration tests for FastAPI endpoints for performances."""

from unittest.mock import AsyncMock, patch

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.performances import Performance
from music_catalogue.models.responses.references import PerformanceRef


class TestPerformanceEndpoints:
    """Integration tests for performance endpoints."""

    def test_get_performance_by_id_success(self, test_client):
        """GET /performances/{id} returns serialized Performance when found."""
        performance = Performance(id="perf-1", name="Wembley")

        with patch(
            "music_catalogue.routers.performances.Performance.get_by_id", new_callable=AsyncMock
        ) as mock_get_by_id:
            mock_get_by_id.return_value = performance

            response = test_client.get("/performances/perf-1")

            assert response.status_code == 200
            assert response.json() == performance.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("perf-1")

    def test_get_performance_by_id_not_found(self, test_client):
        """Not found results propagate as 404 responses."""
        with patch(
            "music_catalogue.routers.performances.Performance.get_by_id", new_callable=AsyncMock
        ) as mock_get_by_id:
            mock_get_by_id.return_value = None
            response = test_client.get("/performances/missing")
            assert response.status_code == 404

    def test_get_performance_by_id_api_error(self, test_client):
        """API errors surface as 500 responses for get by ID."""
        with patch(
            "music_catalogue.routers.performances.Performance.get_by_id", new_callable=AsyncMock
        ) as mock_get_by_id:
            mock_get_by_id.side_effect = APIError("DB failure")

            response = test_client.get("/performances/perf-1")

            assert response.status_code == 500
            assert "DB failure" in response.json()["detail"]

    def test_search_performances_success(self, test_client):
        """GET /performances with valid query returns PerformanceRef list."""
        query = "wembley"
        results = [
            PerformanceRef(id="perf-1", name="Wembley 2024s", venue="Wembley Stadium", city="London"),
            PerformanceRef(id="perf-2", name="Wembley 2023"),
        ]

        with patch("music_catalogue.routers.performances.Performance.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = results

            response = test_client.get("/performances", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in results]
            mock_search.assert_awaited_once_with(query)

    def test_search_performances_requires_query(self, test_client):
        """Query parameter is mandatory."""
        response = test_client.get("/performances")
        assert response.status_code == 422

    def test_search_performances_query_length_validation(self, test_client):
        """Query length is enforced for performance search."""
        response = test_client.get("/performances", params={"query": "a"})
        assert response.status_code == 422

        response_long = test_client.get("/performances", params={"query": "x" * 51})
        assert response_long.status_code == 422

    def test_search_performances_api_error(self, test_client):
        """API errors surface as 500 responses for search."""
        with patch("music_catalogue.routers.performances.Performance.search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = APIError("Search failure")

            response = test_client.get("/performances", params={"query": "test"})

            assert response.status_code == 500
            assert "Search failure" in response.json()["detail"]

    def test_create_performance_success(self, test_client):
        """POST /performances returns created performance payload."""
        payload = {"name": "New Concert", "venue": "Wembley Stadium", "city": "London"}
        performance = Performance(id="perf-123", name="New Concert", venue="Wembley Stadium", city="London")

        with patch("music_catalogue.routers.performances.Performance.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = performance

            response = test_client.post("/performances", json=payload)

            assert response.status_code == 201
            assert response.json() == performance.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()

    def test_create_performance_with_nested_data(self, test_client, sample_uuid):
        """POST /performances accepts nested artists and works."""
        payload = {
            "name": "Full Concert",
            "artists": [
                {"artist_id": sample_uuid, "role": "headliner", "billing_order": 1},
            ],
            "works": [
                {"work_id": sample_uuid, "set_order": 1, "set_name": "Main Set"},
            ],
        }
        performance = Performance(id="perf-456", name="Full Concert")

        with patch("music_catalogue.routers.performances.Performance.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = performance

            response = test_client.post("/performances", json=payload)

            assert response.status_code == 201
            mock_create.assert_awaited_once()

    def test_create_performance_validation_error(self, test_client):
        """Missing required fields surface as 422 responses."""
        with patch("music_catalogue.routers.performances.Performance.create", new_callable=AsyncMock):
            response = test_client.post("/performances", json={})
            assert response.status_code == 422

    def test_create_performance_api_error(self, test_client):
        """API errors surface as 500 responses for create."""
        with patch("music_catalogue.routers.performances.Performance.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Insert failure")

            response = test_client.post("/performances", json={"name": "Failing Concert"})

            assert response.status_code == 500
            assert "Insert failure" in response.json()["detail"]
