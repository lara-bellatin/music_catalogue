"""Unit tests for CRUD operations on works CRUD module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from music_catalogue.crud import works
from music_catalogue.models.works import Work


class TestWorksCRUD:
    """Tests for works CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_work_by_id_success(self):
        """Test successfully retrieving a work by ID."""
        mock_work_data = {"work_id": "work-1", "title": "Work 1", "versions": []}
        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[mock_work_data]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse", return_value=MagicMock(spec=Work)) as mock_parse,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await works.get_by_id("work-1")

            assert result is mock_parse.return_value
            mock_parse.assert_called_once_with(Work, mock_work_data)
            mock_supabase.table.assert_called_once_with("works")

    @pytest.mark.asyncio
    async def test_get_work_by_id_not_found(self):
        """Test retrieving a work that doesn't exist."""
        work_id = "nonexistent-id"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            res = await works.get_by_id(work_id)
            assert res is None

    @pytest.mark.asyncio
    async def test_search_works_success(self):
        """Test searching for works with a valid query."""
        query = "nielsen"
        mock_results = [
            {"work_id": "id1", "title": "Saul og David"},
            {"work_id": "id2", "title": "Maskarade"},
        ]

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_results))
        mock_supabase.table.return_value = query_builder

        parsed_works = [MagicMock(spec=Work) for _ in mock_results]

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse_list", return_value=parsed_works) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await works.search(query)

            assert result is parsed_works
            mock_parse_list.assert_called_once_with(Work, mock_results)
            query_builder.text_search.assert_called_once_with("search_text", query.replace(" ", "+"))

    @pytest.mark.asyncio
    async def test_search_works_empty_results(self):
        """Test searching for works with no matches."""
        query = "nonexistent composer"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse_list", return_value=[]) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await works.search(query)

            assert result == []
            mock_parse_list.assert_called_once_with(Work, [])

    @pytest.mark.asyncio
    async def test_search_works_query_normalization(self):
        """Test that search query spaces are normalized to +."""
        query = "nielsen saul and david"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse_list", return_value=[]),
        ):
            mock_get_supabase.return_value = mock_supabase

            await works.search(query)

            query_builder.text_search.assert_called_once_with("search_text", "nielsen+saul+and+david")
