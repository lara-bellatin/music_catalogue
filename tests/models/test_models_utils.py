import pytest
from pydantic import BaseModel

from music_catalogue.models.utils import (
    EntityType,
    UnifiedSearchResult,
    _parse,
    _parse_list,
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
