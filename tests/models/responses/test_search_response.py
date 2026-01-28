import pytest

from music_catalogue.models.responses.search import UnifiedSearchResult
from music_catalogue.models.types import EntityType


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
