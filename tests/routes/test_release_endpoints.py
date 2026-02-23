"""Integration tests for FastAPI endpoints for releases."""

from unittest.mock import AsyncMock, patch

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.references import ReleaseRef
from music_catalogue.models.responses.releases import Release


class TestReleaseEndpoints:
    """Integration tests for release endpoints."""

    def test_get_release_by_id_success(self, test_client):
        """GET /releases/{id} returns serialized Release when found."""
        release = Release(id="rel-1", title="Abbey Road", total_tracks=17)

        with patch("music_catalogue.routers.releases.Release.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = release

            response = test_client.get("/releases/rel-1")

            assert response.status_code == 200
            assert response.json() == release.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("rel-1")

    def test_get_release_by_id_not_found(self, test_client):
        """Not found results propagate as 404 responses."""
        with patch("music_catalogue.routers.releases.Release.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None
            response = test_client.get("/releases/missing")
            assert response.status_code == 404

    def test_get_release_by_id_api_error(self, test_client):
        """API errors surface as 500 responses for get by ID."""
        with patch("music_catalogue.routers.releases.Release.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.side_effect = APIError("DB failure")

            response = test_client.get("/releases/rel-1")

            assert response.status_code == 500
            assert "DB failure" in response.json()["detail"]

    def test_search_releases_success(self, test_client):
        """GET /releases with valid query returns ReleaseRef list."""
        query = "abbey"
        results = [
            ReleaseRef(id="rel-1", title="Abbey Road", release_category="album"),
            ReleaseRef(id="rel-2", title="Abbey Road Remaster"),
        ]

        with patch("music_catalogue.routers.releases.Release.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = results

            response = test_client.get("/releases", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in results]
            mock_search.assert_awaited_once_with(query)

    def test_search_releases_requires_query(self, test_client):
        """Query parameter is mandatory."""
        response = test_client.get("/releases")
        assert response.status_code == 422

    def test_search_releases_query_length_validation(self, test_client):
        """Query length is enforced for release search."""
        response = test_client.get("/releases", params={"query": "a"})
        assert response.status_code == 422

        response_long = test_client.get("/releases", params={"query": "x" * 51})
        assert response_long.status_code == 422

    def test_search_releases_api_error(self, test_client):
        """API errors surface as 500 responses for search."""
        with patch("music_catalogue.routers.releases.Release.search", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = APIError("Search failure")

            response = test_client.get("/releases", params={"query": "test"})

            assert response.status_code == 500
            assert "Search failure" in response.json()["detail"]

    def test_create_release_success(self, test_client):
        """POST /releases returns created release payload."""
        payload = {"title": "New Album", "total_tracks": 12}
        release = Release(id="rel-123", title="New Album", total_tracks=12)

        with patch("music_catalogue.routers.releases.Release.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = release

            response = test_client.post("/releases", json=payload)

            assert response.status_code == 201
            assert response.json() == release.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()

    def test_create_release_with_nested_data(self, test_client, sample_uuid):
        """POST /releases accepts nested media items and tracks."""
        payload = {
            "title": "Full Album",
            "media_items": [
                {"medium_type": "digital", "format_name": "FLAC"},
            ],
            "tracks": [
                {"version_id": sample_uuid, "track_number": 1},
            ],
        }
        release = Release(id="rel-456", title="Full Album", total_tracks=1)

        with patch("music_catalogue.routers.releases.Release.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = release

            response = test_client.post("/releases", json=payload)

            assert response.status_code == 201
            mock_create.assert_awaited_once()

    def test_create_release_validation_error(self, test_client):
        """Missing required fields surface as 422 responses."""
        with patch("music_catalogue.routers.releases.Release.create", new_callable=AsyncMock):
            response = test_client.post("/releases", json={})
            assert response.status_code == 422

    def test_create_release_api_error(self, test_client):
        """API errors surface as 500 responses for create."""
        with patch("music_catalogue.routers.releases.Release.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Insert failure")

            response = test_client.post("/releases", json={"title": "Failing Album"})

            assert response.status_code == 500
            assert "Insert failure" in response.json()["detail"]
