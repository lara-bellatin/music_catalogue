import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.person_create import PersonCreate


class TestPersonCreateValidation:
    """Tests for PersonCreate.validate."""

    def test_validate_person_without_death_date_success(self):
        PersonCreate(
            legal_name="Living Composer",
            birth_date="1980-01-01",
        )

    def test_validate_person_with_valid_dates_success(self):
        PersonCreate(
            legal_name="Historic Composer",
            birth_date="1900-01-01",
            death_date="1950-12-31",
        )

    def test_validate_person_with_invalid_date_order_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(
                legal_name="Invalid Dates",
                birth_date="2000-01-01",
                death_date="1990-01-01",
            )

        assert "Start date" in str(exc_info.value) or "Invalid dates" in str(exc_info.value)

    def test_validate_person_with_invalid_format_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(
                legal_name="Wrong Format",
                birth_date="01-01-1980",
            )

        assert "Invalid" in str(exc_info.value)

    def test_validate_person_with_future_dates_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PersonCreate(
                legal_name="Future Person",
                birth_date="2999-01-01",
            )

        assert "future" in str(exc_info.value).lower()
