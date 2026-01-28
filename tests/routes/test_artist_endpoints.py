"""Integration tests for FastAPI endpoints matching the current API behavior for artists."""

from unittest.mock import AsyncMock, patch

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.artists import Artist
from music_catalogue.models.responses.persons import Person
from music_catalogue.models.types import ArtistType


class TestArtistsEndpoints:
    """Integration tests for artists endpoints."""

    def test_get_artist_by_id_success(self, test_client):
        """GET /artists/{id} returns serialized Artist when found."""
        artist = Artist(id="artist-1", display_name="Carl Nielsen", artist_type=ArtistType.SOLO)

        with patch("music_catalogue.routers.artists.artists.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = artist

            response = test_client.get("/artists/artist-1")

            assert response.status_code == 200
            assert response.json() == artist.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("artist-1")

    def test_get_artist_by_id_not_found(self, test_client):
        """Not found results propagate as 404 responses."""
        with patch("music_catalogue.routers.artists.artists.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None
            response = test_client.get("/artists/missing")
            assert response.status_code == 404

    def test_search_artists_success(self, test_client):
        """GET /artists with valid query returns mixed entity list."""
        query = "nielsen"
        mock_results = [Artist(id="artist-1", display_name="Carl Nielsen", artist_type=ArtistType.SOLO)]

        with patch("music_catalogue.routers.artists.artists.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results

            response = test_client.get("/artists", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in mock_results]
            mock_search.assert_awaited_once_with(query)

    def test_search_artists_requires_query(self, test_client):
        """Query parameter is mandatory for artists search."""
        response = test_client.get("/artists")

        assert response.status_code == 422

    def test_search_artists_query_length_validation(self, test_client):
        """Query length is enforced for artists search."""
        response_short = test_client.get("/artists", params={"query": "a"})

        assert response_short.status_code == 422

        response_long = test_client.get("/artists", params={"query": "x" * 51})

        assert response_long.status_code == 422

    def test_create_artist_success(self, test_client, sample_uuid):
        """POST /artists returns created artist payload."""
        payload = {"display_name": "New Artist", "artist_type": ArtistType.SOLO, "person_id": sample_uuid}
        person = Person(id=sample_uuid, legal_name="Artist Person")
        artist = Artist(id="artist-123", display_name="New Artist", artist_type=ArtistType.SOLO, person=person)

        with (
            patch("music_catalogue.routers.artists.artists.create", new_callable=AsyncMock) as mock_create,
        ):
            mock_create.return_value = artist

            response = test_client.post("/artists", json=payload)

            assert response.status_code == 201
            assert response.json() == artist.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()

    def test_create_artist_validation_error(self, test_client):
        """Domain validation errors surface as 422 responses."""
        with patch("music_catalogue.routers.artists.artists.create", new_callable=AsyncMock):
            response = test_client.post("/artists", json={"display_name": "Invalid", "artist_type": ArtistType.SOLO})

            assert response.status_code == 422

    def test_create_artist_api_error(self, test_client, sample_uuid):
        """API errors surface as 500 responses for create."""
        with patch("music_catalogue.routers.artists.artists.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Upstream failure")

            response = test_client.post(
                "/artists", json={"display_name": "Artist", "artist_type": ArtistType.SOLO, "person_id": sample_uuid}
            )

            assert response.status_code == 500
            assert "Upstream failure" in response.json()["detail"]
