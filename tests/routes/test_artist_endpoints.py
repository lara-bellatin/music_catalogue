"""Integration tests for FastAPI endpoints matching the current API behavior."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from music_catalogue.main import app
from music_catalogue.models.artists import Artist, ArtistType


class TestArtistsEndpoints:
    """Integration tests for artists endpoints."""

    def test_get_artist_by_id_success(self):
        """GET /artists/{id} returns serialized Artist when found."""
        client = TestClient(app)
        artist = Artist(id="artist-1", display_name="Carl Nielsen", artist_type=ArtistType.SOLO)

        with patch("music_catalogue.routers.artists.artists.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = artist

            response = client.get("/artists/artist-1")

            assert response.status_code == 200
            assert response.json() == artist.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("artist-1")

    def test_get_artist_by_id_not_found(self):
        """Uncaught errors propagate as 500 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.artists.artists.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.side_effect = IndexError()

            response = client.get("/artists/missing")

            assert response.status_code == 500

    def test_search_artists_success(self):
        """GET /artists with valid query returns mixed entity list."""
        client = TestClient(app)
        query = "nielsen"
        mock_results = [Artist(id="artist-1", display_name="Carl Nielsen", artist_type=ArtistType.SOLO)]

        with patch("music_catalogue.routers.artists.artists.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results

            response = client.get("/artists", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in mock_results]
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
