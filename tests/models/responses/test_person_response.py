from datetime import date

import pytest

from music_catalogue.models.responses.persons import Person


class TestPerson:
    """Test the Person Model"""

    def test_person_from_dict_full_payload(self):
        payload = {
            "person_id": "person-1",
            "legal_name": "John Smith",
            "birth_date": "1980-05-12",
            "death_date": "2020-01-01",
            "pronouns": "he/him",
            "notes": "Composer",
        }

        person = Person.from_dict(payload)

        assert person.id == "person-1"
        assert person.legal_name == "John Smith"
        assert person.birth_date == date(1980, 5, 12)
        assert person.death_date == date(2020, 1, 1)
        assert person.pronouns == "he/him"
        assert person.notes == "Composer"

    def test_person_from_dict_handles_missing_optional_fields(self):
        payload = {
            "person_id": "person-2",
            "legal_name": "Jane Doe",
            "birth_date": None,
            "death_date": None,
        }

        person = Person.from_dict(payload)

        assert person.id == "person-2"
        assert person.legal_name == "Jane Doe"
        assert person.birth_date is None
        assert person.death_date is None
        assert person.pronouns is None
        assert person.notes is None

    def test_person_from_dict_handles_missing_required_fields(self):
        payload = {
            "person_id": None,
            "legal_name": "Jane Doe",
            "birth_date": None,
            "death_date": None,
        }

        with pytest.raises(ValueError):
            Person.from_dict(payload)
