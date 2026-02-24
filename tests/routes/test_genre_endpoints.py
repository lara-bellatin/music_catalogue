"""Integration tests for FastAPI endpoints for genres."""

from unittest.mock import AsyncMock, patch

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.genres import Genre


class TestGenreEndpoints:
    """Integration tests for genre endpoints."""

    def test_get_genre_by_id_success(self, test_client):
        """GET /genres/{id} returns serialized Genre when found."""
        genre = Genre(id="genre-1", name="Jazz", description="A genre of music")

        with patch("music_catalogue.routers.genres.Genre.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = genre

            response = test_client.get("/genres/genre-1")

            assert response.status_code == 200
            assert response.json() == genre.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("genre-1")

    def test_get_genre_by_id_not_found(self, test_client):
        """Not found results propagate as 404 responses."""
        with patch("music_catalogue.routers.genres.Genre.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None
            response = test_client.get("/genres/missing")
            assert response.status_code == 404

    def test_get_genre_by_id_api_error(self, test_client):
        """API errors surface as 500 responses for get by ID."""
        with patch("music_catalogue.routers.genres.Genre.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.side_effect = APIError("DB failure")

            response = test_client.get("/genres/genre-1")

            assert response.status_code == 500
            assert "DB failure" in response.json()["detail"]

    def test_search_genres_success(self, test_client):
        """GET /genres with valid query returns Genre list."""
        query = "jazz"
        results = [
            Genre(id="genre-1", name="Jazz", description="A genre of music"),
            Genre(id="genre-2", name="Jazz Fusion"),
        ]

        with patch("music_catalogue.routers.genres.Genre.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = results

            response = test_client.get("/genres", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in results]
            mock_search.assert_awaited_once_with(query)

    def test_search_genres_requires_query(self, test_client):
        """Query parameter is mandatory."""
        response = test_client.get("/genres")
        assert response.status_code == 422

    def test_search_genres_query_length_validation(self, test_client):
        """Query length is enforced for genre search."""
        response = test_client.get("/genres", params={"query": "a"})
        assert response.status_code == 422

        response_long = test_client.get("/genres", params={"query": "x" * 51})
        assert response_long.status_code == 422

    def test_search_genres_api_error(self, test_client):
        """API errors surface as 500 responses for search."""
        with patch("music_catalogue.routers.genres.Genre.search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = APIError("Search failure")

            response = test_client.get("/genres", params={"query": "test"})

            assert response.status_code == 500
            assert "Search failure" in response.json()["detail"]

    def test_create_genre_success(self, test_client):
        """POST /genres returns created genre payload."""
        payload = {"name": "Rock", "description": "Rock music"}
        genre = Genre(id="genre-123", name="Rock", description="Rock music")

        with patch("music_catalogue.routers.genres.Genre.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = genre

            response = test_client.post("/genres", json=payload)

            assert response.status_code == 201
            assert response.json() == genre.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()

    def test_create_genre_validation_error(self, test_client):
        """Missing required fields surface as 422 responses."""
        with patch("music_catalogue.routers.genres.Genre.create", new_callable=AsyncMock):
            response = test_client.post("/genres", json={})
            assert response.status_code == 422

    def test_create_genre_api_error(self, test_client):
        """API errors surface as 500 responses for create."""
        with patch("music_catalogue.routers.genres.Genre.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Insert failure")

            response = test_client.post("/genres", json={"name": "Failing Genre"})

            assert response.status_code == 500
            assert "Insert failure" in response.json()["detail"]
