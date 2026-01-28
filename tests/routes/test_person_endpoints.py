"""Integration tests for FastAPI endpoints matching the current API behavior for persons."""

from unittest.mock import AsyncMock, patch

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.persons import Person


class TestPersonEndpoints:
    """Integration tests for person endpoints."""

    def test_get_person_by_id_success(self, test_client, sample_uuid):
        """GET /persons/{id} returns serialized Person when found."""
        person = Person(id=sample_uuid, legal_name="Carl Nielsen")

        with patch("music_catalogue.routers.persons.persons.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = person

            response = test_client.get(f"/persons/{sample_uuid}")

            assert response.status_code == 200
            assert response.json() == person.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with(sample_uuid)

    def test_get_person_by_id_not_found(self, test_client):
        """Not found results propagate as 404 responses."""
        with patch("music_catalogue.routers.persons.persons.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = None
            response = test_client.get("/persons/missing")
            assert response.status_code == 404

    def test_search_persons_success(self, test_client):
        """GET /persons with valid query returns mixed entity list."""
        query = "nielsen"
        mock_results = [Person(id="person-1", legal_name="Carl Nielsen")]

        with patch("music_catalogue.routers.persons.persons.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results

            response = test_client.get("/persons", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in mock_results]
            mock_search.assert_awaited_once_with(query)

    def test_search_persons_requires_query(self, test_client):
        """Query parameter is mandatory for persons search."""
        response = test_client.get("/persons")

        assert response.status_code == 422

    def test_search_persons_query_length_validation(self, test_client):
        """Query length is enforced for persons search."""
        response_short = test_client.get("/persons", params={"query": "a"})

        assert response_short.status_code == 422

        response_long = test_client.get("/persons", params={"query": "x" * 51})

        assert response_long.status_code == 422

    def test_create_person_success(self, test_client):
        """POST /persons returns created person payload."""
        payload = {
            "legal_name": "New Composer",
            "birth_date": "1985-05-05",
        }
        person = Person(id="person-123", legal_name="New Composer")

        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = person

            response = test_client.post("/persons", json=payload)

            assert response.status_code == 201
            assert response.json() == person.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()

    def test_create_person_validation_error(self, test_client):
        """Domain validation errors surface as 422 responses."""
        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock):
            response = test_client.post("/persons", json={})

            assert response.status_code == 422

    def test_create_person_api_error(self, test_client):
        """API errors surface as 500 responses for create."""
        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Upstream failure")

            response = test_client.post("/persons", json={"legal_name": "Composer"})

            assert response.status_code == 500
            assert "Upstream failure" in response.json()["detail"]

    def test_bulk_create_persons_success(self, test_client):
        """POST /persons/bulk returns list of created persons."""
        payload = [
            {"legal_name": "Member One"},
            {"legal_name": "Member Two", "birth_date": "1990-01-01"},
        ]
        people = [
            Person(id="person-1", legal_name="Member One"),
            Person(id="person-2", legal_name="Member Two"),
        ]

        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = people

            response = test_client.post("/persons/bulk", json=payload)

            assert response.status_code == 201
            assert response.json() == [person.model_dump(exclude_none=True) for person in people]
            assert mock_create.await_count == len(payload)

    def test_bulk_create_persons_api_error(self, test_client):
        """API errors propagate during bulk create."""
        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Bulk failure")

            response = test_client.post("/persons/bulk", json=[{"legal_name": "Person"}])

            assert response.status_code == 500
            assert "Bulk failure" in response.json()["detail"]
