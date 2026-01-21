import uuid

import pytest
from pydantic import BaseModel

from music_catalogue.models.exceptions import ValidationError
from music_catalogue.models.utils import (
    EntityType,
    UnifiedSearchResult,
    _parse,
    _parse_list,
    validate_start_and_end_dates,
    validate_start_and_end_years,
    validate_uuid,
)


class DummyModel(BaseModel):
    value: str

    @classmethod
    def from_dict(cls, data):
        return cls(value=data["value"])


class TestUnifiedSearchResult:
    """Test the UnifiedSearchResult model"""

    def test_unified_search_result_from_dict_success(self):
        payload = {
            "entity_type": "work",
            "entity_id": "work-1",
            "display_text": "Test Work",
            "rank": 0.1,
        }

        result = UnifiedSearchResult.from_dict(payload)

        assert result.entity_type is EntityType.WORK
        assert result.entity_id == "work-1"
        assert result.display_text == "Test Work"
        assert result.rank == pytest.approx(0.1)

    def test_unified_search_result_from_dict_invalid_type(self):
        payload = {
            "entity_type": "invalid",
            "entity_id": "bad",
            "display_text": "Bad Data",
            "rank": 0.0,
        }

        with pytest.raises(ValueError):
            UnifiedSearchResult.from_dict(payload)


class TestModelParsers:
    """Test _parse and _parse_list functions"""

    def test_parse_returns_none_for_empty_input(self):
        result = _parse(DummyModel, None)
        assert result is None

    def test_parse_returns_model_instance(self):
        result = _parse(DummyModel, {"value": "ok"})
        assert isinstance(result, DummyModel)
        assert result.value == "ok"

    def test_parse_list_returns_empty_for_none(self):
        result = _parse_list(DummyModel, None)
        assert result == []

    def test_parse_list_filters_out_empty_items(self):
        items = [{"value": "keep"}, {}]

        result = _parse_list(DummyModel, items)

        assert len(result) == 1
        assert isinstance(result[0], DummyModel)
        assert result[0].value == "keep"

    def test_parse_list_processes_multiple_items(self):
        items = [{"value": "first"}, {"value": "second"}]

        result = _parse_list(DummyModel, items)

        assert [item.value for item in result] == ["first", "second"]


class TestValidateUUID:
    """Tests for validate_uuid helper."""

    def test_valid_uuid_passes(self):
        """A proper UUID string does not raise."""
        validate_uuid(str(uuid.uuid4()))

    def test_invalid_uuid_raises_validation_error(self):
        """Invalid UUID strings raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_uuid("not-a-uuid")


class TestValidateStartAndEndDates:
    """Tests for validate_start_and_end_dates helper."""

    def test_valid_date_range_passes(self):
        """Valid date ranges complete without raising."""
        validate_start_and_end_dates("1900-01-01", "1950-12-31")

    def test_start_after_end_raises_validation_error(self):
        """Start dates after end dates raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_start_and_end_dates("1950-01-01", "1900-01-01")

    def test_future_date_raises_validation_error(self):
        """Future dates are rejected."""
        with pytest.raises(ValidationError):
            validate_start_and_end_dates("2999-01-01", "2999-12-31")

    def test_invalid_date_format_raises_validation_error(self):
        """Non-ISO formatted dates raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_start_and_end_dates("01-01-1900", "12-31-1950")


class TestValidateStartAndEndYears:
    """Tests for validate_start_and_end_years helper."""

    def test_valid_year_range_passes(self):
        """Valid year ranges complete without raising."""
        validate_start_and_end_years(1900, 1950)

    def test_start_year_after_end_year_raises(self):
        """Start years after end years raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_start_and_end_years(2000, 1900)

    def test_future_year_raises_validation_error(self):
        """Years in the future are rejected."""
        with pytest.raises(ValidationError):
            validate_start_and_end_years(2999, 3000)

    def test_invalid_year_value_raises_validation_error(self):
        """Impossible year values surface as ValidationError."""
        with pytest.raises(ValidationError):
            validate_start_and_end_years(123123123, 321321312)
