"""Integration tests for FastAPI endpoints matching the current API behavior."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from music_catalogue.main import app
from music_catalogue.models.exceptions import APIError, ValidationError
from music_catalogue.models.persons import Person


class TestPersonEndpoints:
    """Integration tests for person endpoints."""

    def test_get_person_by_id_success(self):
        """GET /persons/{id} returns serialized Person when found."""
        client = TestClient(app)
        person = Person(id="person-1", legal_name="Carl Nielsen")

        with patch("music_catalogue.routers.persons.persons.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.return_value = person

            response = client.get("/persons/person-1")

            assert response.status_code == 200
            assert response.json() == person.model_dump(exclude_none=True)
            mock_get_by_id.assert_awaited_once_with("person-1")

    def test_get_person_by_id_not_found(self):
        """Uncaught errors propagate as 500 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.persons.persons.get_by_id", new_callable=AsyncMock) as mock_get_by_id:
            mock_get_by_id.side_effect = IndexError()

            response = client.get("/persons/missing")

            assert response.status_code == 500

    def test_search_persons_success(self):
        """GET /persons with valid query returns mixed entity list."""
        client = TestClient(app)
        query = "nielsen"
        mock_results = [Person(id="person-1", legal_name="Carl Nielsen")]

        with patch("music_catalogue.routers.persons.persons.search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results

            response = client.get("/persons", params={"query": query})

            assert response.status_code == 200
            assert response.json() == [item.model_dump(exclude_none=True) for item in mock_results]
            mock_search.assert_awaited_once_with(query)

    def test_search_persons_requires_query(self):
        """Query parameter is mandatory for persons search."""
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/persons")

        assert response.status_code == 422

    def test_search_persons_query_length_validation(self):
        """Query length is enforced for persons search."""
        client = TestClient(app)

        response_short = client.get("/persons", params={"query": "a"})

        assert response_short.status_code == 422

        response_long = client.get("/persons", params={"query": "x" * 51})

        assert response_long.status_code == 422

    def test_create_person_success(self):
        """POST /persons returns created person payload."""
        client = TestClient(app)
        payload = {
            "legal_name": "New Composer",
            "birth_date": "1985-05-05",
        }
        person = Person(id="person-123", legal_name="New Composer")

        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = person

            response = client.post("/persons", json=payload)

            assert response.status_code == 201
            assert response.json() == person.model_dump(exclude_none=True)
            mock_create.assert_awaited_once()
            forwarded_payload = mock_create.await_args.args[0].model_dump(exclude_none=True)
            assert forwarded_payload == payload

    def test_create_person_validation_error(self):
        """Domain validation errors surface as 400 responses."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = ValidationError("Invalid chronology")

            response = client.post("/persons", json={"legal_name": "Invalid"})

            assert response.status_code == 400
            assert "Invalid chronology" in response.json()["detail"]

    def test_create_person_api_error(self):
        """API errors surface as 500 responses for create."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Upstream failure")

            response = client.post("/persons", json={"legal_name": "Composer"})

            assert response.status_code == 500
            assert "Upstream failure" in response.json()["detail"]

    def test_bulk_create_persons_success(self):
        """POST /persons/bulk returns list of created persons."""
        client = TestClient(app)
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

            response = client.post("/persons/bulk", json=payload)

            assert response.status_code == 201
            assert response.json() == [person.model_dump(exclude_none=True) for person in people]
            assert mock_create.await_count == len(payload)
            forwarded_payloads = [args.args[0].model_dump(exclude_none=True) for args in mock_create.await_args_list]
            assert forwarded_payloads == payload

    def test_bulk_create_persons_api_error(self):
        """API errors propagate during bulk create."""
        client = TestClient(app, raise_server_exceptions=False)

        with patch("music_catalogue.routers.persons.persons.create", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = APIError("Bulk failure")

            response = client.post("/persons/bulk", json=[{"legal_name": "Person"}])

            assert response.status_code == 500
            assert "Bulk failure" in response.json()["detail"]
