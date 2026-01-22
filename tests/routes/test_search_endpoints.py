"""Integration tests for FastAPI endpoints matching the current API behavior for search."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from music_catalogue.main import app
from music_catalogue.models.utils import EntityType, UnifiedSearchResult


class TestSearchEndpoints:
    """Integration tests for unified search endpoints."""

    def test_search_all_success(self):
        """Search across all entities with filters returns serialized results."""
        client = TestClient(app)
        query = "nielsen"
        mock_results = [
            UnifiedSearchResult(
                entity_type=EntityType.WORK,
                entity_id="work-1",
                display_text="Saul og David",
                rank=0.9,
            ),
            UnifiedSearchResult(
                entity_type=EntityType.ARTIST,
                entity_id="artist-1",
                display_text="Carl Nielsen",
                rank=0.9,
            ),
        ]

        with patch("music_catalogue.main.unified_search", new_callable=AsyncMock) as mock_unified_search:
            mock_unified_search.return_value = mock_results

            response = client.get(
                "/search",
                params={"query": query, "limit": 10},
            )

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in mock_results]
            mock_unified_search.assert_awaited_once_with(query, [], 10)

    def test_search_limited_entities_success(self):
        """Search across all entities with filters returns serialized results."""
        client = TestClient(app)
        query = "nielsen"
        mock_results = [
            UnifiedSearchResult(
                entity_type=EntityType.WORK,
                entity_id="work-1",
                display_text="Saul og David",
                rank=0.9,
            ),
        ]

        with patch("music_catalogue.main.unified_search", new_callable=AsyncMock) as mock_unified_search:
            mock_unified_search.return_value = mock_results

            response = client.get(
                "/search",
                params={"query": query, "entity_types": [EntityType.WORK.value], "limit": 10},
            )

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in mock_results]
            mock_unified_search.assert_awaited_once_with(query, [EntityType.WORK], 10)

    def test_search_all_invalid_limit(self):
        """Requests exceeding limit validation are rejected."""
        client = TestClient(app)

        response = client.get("/search", params={"query": "nielsen", "limit": 101})

        assert response.status_code == 422

    def test_search_all_no_entity_filters(self):
        """Search defaults to all entity types when filter absent."""
        client = TestClient(app)
        query = "beethoven"
        mock_results = []

        with patch("music_catalogue.main.unified_search", new_callable=AsyncMock) as mock_unified_search:
            mock_unified_search.return_value = mock_results

            response = client.get("/search", params={"query": query})

            assert response.status_code == 200
            assert response.json() == []
            mock_unified_search.assert_awaited_once_with(query, [], 20)

    def test_search_all_query_length_validation(self):
        """Query length is enforced for unified search."""
        client = TestClient(app)

        response = client.get("/search", params={"query": "a"})

        assert response.status_code == 422

        response_long = client.get("/search", params={"query": "x" * 51})

        assert response_long.status_code == 422
