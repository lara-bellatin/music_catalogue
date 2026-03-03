"""
Unit tests for CRUD operations on unified search.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from music_catalogue.crud.search import unified_search
from music_catalogue.models.responses.search import PaginatedSearchResponse, UnifiedSearchResult
from music_catalogue.models.types import EntityType


class TestUnifiedSearch:
    """Tests for unified search operation."""

    @pytest.mark.asyncio
    async def test_unified_search_success(self):
        """Test successfully querying a list of entities."""
        search_query = "test"
        search_limit = 20
        mock_search_data = [
            {"entity_type": "work", "entity_id": "work-1", "display_text": "Test Work", "rank": 0.1, "total_count": 2},
            {
                "entity_type": "artist",
                "entity_id": "artist-1",
                "display_text": "Test Artist",
                "rank": 0.1,
                "total_count": 2,
            },
        ]
        mock_parsed = [
            UnifiedSearchResult(entity_type=EntityType.WORK, entity_id="work-1", display_text="Test Work", rank=0.1),
            UnifiedSearchResult(
                entity_type=EntityType.ARTIST, entity_id="artist-1", display_text="Test Artist", rank=0.1
            ),
        ]
        mock_supabase = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.select.return_value = mock_rpc
        mock_rpc.execute = AsyncMock(return_value=MagicMock(data=mock_search_data))
        mock_supabase.rpc = MagicMock(return_value=mock_rpc)

        with (
            patch("music_catalogue.crud.search.get_supabase", AsyncMock(return_value=mock_supabase)),
            patch("music_catalogue.crud.search._parse_list", return_value=mock_parsed) as mock_parse,
        ):
            result = await unified_search(search_query, limit=search_limit)

            mock_supabase.rpc.assert_called_once_with(
                "unified_search", {"query_text": search_query, "fetch_limit": search_limit, "fetch_offset": 0}
            )
            mock_rpc.select.assert_called_once_with("*")
            mock_rpc.execute.assert_awaited_once()
            mock_parse.assert_called_once_with(UnifiedSearchResult, mock_search_data)
            assert isinstance(result, PaginatedSearchResponse)
            assert result.results == mock_parsed
            assert result.total_count == 2
            assert result.limit == search_limit
            assert result.offset == 0

    @pytest.mark.asyncio
    async def test_unified_search_empty(self):
        """Test querying a list of entities but return empty array."""
        search_query = "test"
        search_limit = 20
        mock_supabase = MagicMock()
        mock_rpc = MagicMock()
        mock_rpc.select.return_value = mock_rpc
        mock_rpc.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.rpc = MagicMock(return_value=mock_rpc)

        with (
            patch("music_catalogue.crud.search.get_supabase", AsyncMock(return_value=mock_supabase)),
            patch("music_catalogue.crud.search._parse_list", return_value=[]) as mock_parse,
        ):
            result = await unified_search(search_query, limit=search_limit)

            mock_supabase.rpc.assert_called_once_with(
                "unified_search", {"query_text": search_query, "fetch_limit": search_limit, "fetch_offset": 0}
            )
            mock_rpc.select.assert_called_once_with("*")
            mock_rpc.execute.assert_awaited_once()
            mock_parse.assert_called_once_with(UnifiedSearchResult, [])
            assert isinstance(result, PaginatedSearchResponse)
            assert result.results == []
            assert result.total_count == 0
            assert result.limit == search_limit
            assert result.offset == 0
