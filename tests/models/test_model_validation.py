import uuid

import pytest

from music_catalogue.models.validation import (
    validate_start_and_end_dates,
    validate_start_and_end_years,
    validate_uuid,
)


class TestValidateUUID:
    """Tests for validate_uuid helper."""

    def test_valid_uuid_passes(self):
        """A proper UUID string does not raise."""
        validate_uuid(str(uuid.uuid4()))

    def test_invalid_uuid_raises_value_error(self):
        """Invalid UUID strings raise ValueError."""
        with pytest.raises(ValueError):
            validate_uuid("not-a-uuid")


class TestValidateStartAndEndDates:
    """Tests for validate_start_and_end_dates helper."""

    def test_valid_date_range_passes(self):
        """Valid date ranges complete without raising."""
        validate_start_and_end_dates("1900-01-01", "1950-12-31")

    def test_start_after_end_raises_value_error(self):
        """Start dates after end dates raise ValueError."""
        with pytest.raises(ValueError):
            validate_start_and_end_dates("1950-01-01", "1900-01-01")

    def test_future_date_raises_value_error(self):
        """Future dates are rejected."""
        with pytest.raises(ValueError):
            validate_start_and_end_dates("2999-01-01", "2999-12-31")

    def test_invalid_date_format_raises_value_error(self):
        """Non-ISO formatted dates raise ValueError."""
        with pytest.raises(ValueError):
            validate_start_and_end_dates("01-01-1900", "12-31-1950")


class TestValidateStartAndEndYears:
    """Tests for validate_start_and_end_years helper."""

    def test_valid_year_range_passes(self):
        """Valid year ranges complete without raising."""
        validate_start_and_end_years(1900, 1950)

    def test_start_year_after_end_year_raises(self):
        """Start years after end years raise ValueError."""
        with pytest.raises(ValueError):
            validate_start_and_end_years(2000, 1900)

    def test_future_year_raises_value_error(self):
        """Years in the future are rejected."""
        with pytest.raises(ValueError):
            validate_start_and_end_years(2999, 3000)

    def test_invalid_year_value_raises_value_error(self):
        """Impossible year values surface as ValueError."""
        with pytest.raises(ValueError):
            validate_start_and_end_years(123123123, 321321312)
