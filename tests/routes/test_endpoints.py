"""Integration tests for FastAPI endpoints matching the current API behavior."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from music_catalogue.main import app
from music_catalogue.models import Artist, EntityType, Person, UnifiedSearchResult, Work
from music_catalogue.models.artists import ArtistType


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


class TestWorksEndpoints:
    """Integration tests for works endpoints."""

    def test_get_work_by_id_success(self):
        """GET /works/{id} returns serialized Work when found."""
        client = TestClient(app)
        work = Work(id="work-1", title="Saul og David")

        with patch("music_catalogue.main.works.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = work

            response = client.get("/works/work-1")

            assert response.status_code == 200
            assert response.json() == work.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("work-1")

    def test_get_work_by_id_not_found(self):
        """Uncaught errors propagate as 500 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.main.works.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
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

        with patch("music_catalogue.main.works.search", new_callable=AsyncMock) as mock_search:
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


class TestArtistsEndpoints:
    """Integration tests for artists endpoints."""

    def test_get_artist_by_id_success(self):
        """GET /artists/{id} returns serialized Artist when found."""
        client = TestClient(app)
        artist = Artist(id="artist-1", display_name="Carl Nielsen", artist_type=ArtistType.SOLO)

        with patch("music_catalogue.main.artists.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = artist

            response = client.get("/artists/artist-1")

            assert response.status_code == 200
            assert response.json() == artist.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("artist-1")

    def test_get_artist_by_id_not_found(self):
        """Uncaught errors propagate as 500 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.main.artists.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.side_effect = IndexError()

            response = client.get("/artists/missing")

            assert response.status_code == 500

    def test_search_artists_success(self):
        """GET /artists with valid query returns mixed entity list."""
        client = TestClient(app)
        query = "nielsen"
        artist = Artist(id="artist-1", display_name="Carl Nielsen", artist_type=ArtistType.SOLO)
        person = Person(id="person-1", legal_name="Anne-Marie Carl Nielsen")

        with patch("music_catalogue.main.artists.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [artist, person]

            response = client.get("/artists", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [artist.model_dump(exclude_none=True), person.model_dump(exclude_none=True)]
            mock_search.assert_awaited_once_with(query)

    def test_search_artists_requires_query(self):
        """Query parameter is mandatory for artists search."""
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/artists")

        assert response.status_code == 422

    def test_search_artists_query_length_validation(self):
        """Query length is enforced for artists search."""
        client = TestClient(app)

        response_short = client.get("/artists", params={"query": "a"})

        assert response_short.status_code == 422

        response_long = client.get("/artists", params={"query": "x" * 51})

        assert response_long.status_code == 422
