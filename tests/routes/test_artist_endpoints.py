"""Integration tests for FastAPI endpoints matching the current API behavior for artists."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from music_catalogue.main import app
from music_catalogue.models.artists import Artist, ArtistType
from music_catalogue.models.exceptions import APIError, ValidationError
from music_catalogue.models.persons import Person


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

    def test_create_artist_success(self):
        """POST /artists returns created artist payload."""
        client = TestClient(app)
        payload = {"display_name": "New Artist", "artist_type": ArtistType.SOLO, "person_id": "person-123"}
        person = Person(id="person-123", legal_name="Artist Person")
        artist = Artist(id="artist-123", display_name="New Artist", artist_type=ArtistType.SOLO, person=person)

        with patch("music_catalogue.routers.artists.artists.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = artist

            response = client.post("/artists", json=payload)

            assert response.status_code == 201
            assert response.json() == artist.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()
            forwarded_payload = mock_create.await_args.args[0].model_dump(exclude_none=True)
            assert forwarded_payload == payload

    def test_create_artist_validation_error(self):
        """Domain validation errors surface as 400 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.artists.artists.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValidationError("Invalid")

            response = client.post("/artists", json={"display_name": "Invalid", "artist_type": ArtistType.SOLO})

            assert response.status_code == 400
            assert "Invalid" in response.json()["detail"]

    def test_create_artist_api_error(self):
        """API errors surface as 500 responses for create."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.artists.artists.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Upstream failure")

            response = client.post("/artists", json={"display_name": "Artist", "artist_type": ArtistType.SOLO})

            assert response.status_code == 500
            assert "Upstream failure" in response.json()["detail"]
