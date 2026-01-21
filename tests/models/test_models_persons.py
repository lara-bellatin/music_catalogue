from datetime import date

import pytest

from music_catalogue.models.exceptions import ValidationError
from music_catalogue.models.persons import Person, PersonCreate


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


class TestPersonCreateValidation:
    """Tests for PersonCreate.validate."""

    def test_validate_person_without_death_date_success(self):
        person = PersonCreate(
            legal_name="Living Composer",
            birth_date="1980-01-01",
        )

        person.validate()

    def test_validate_person_with_valid_dates_success(self):
        person = PersonCreate(
            legal_name="Historic Composer",
            birth_date="1900-01-01",
            death_date="1950-12-31",
        )

        person.validate()

    def test_validate_person_with_invalid_date_order_raises(self):
        person = PersonCreate(
            legal_name="Invalid Dates",
            birth_date="2000-01-01",
            death_date="1990-01-01",
        )

        with pytest.raises(ValidationError) as exc_info:
            person.validate()

        assert "Start date" in str(exc_info.value) or "Invalid dates" in str(exc_info.value)

    def test_validate_person_with_invalid_format_raises(self):
        person = PersonCreate(
            legal_name="Wrong Format",
            birth_date="01-01-1980",
        )

        with pytest.raises(ValidationError) as exc_info:
            person.validate()

        assert "Invalid" in str(exc_info.value)

    def test_validate_person_with_future_dates_raises(self):
        person = PersonCreate(
            legal_name="Future Person",
            birth_date="2999-01-01",
        )

        with pytest.raises(ValidationError) as exc_info:
            person.validate()

        assert "future" in str(exc_info.value).lower()
