"""Unit tests for CRUD operations on works CRUD module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from music_catalogue.crud import works
from music_catalogue.models.exceptions import ValidationError
from music_catalogue.models.works import Work, WorkCreate, WorkCreditCreate, WorkVersionCreate


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
        query_builder.single.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_work_data))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse", return_value=MagicMock(spec=Work)) as mock_parse,
            patch("music_catalogue.crud.works.validate_uuid", return_value=None) as mock_validate,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await works.get_by_id("work-1")

            mock_validate.assert_called_once_with("work-1")
            mock_supabase.table.assert_called_once_with("works")
            mock_parse.assert_called_once_with(Work, mock_work_data)
            assert result is mock_parse.return_value

    @pytest.mark.asyncio
    async def test_get_work_by_id_not_found(self):
        """Test retrieving a work that doesn't exist."""
        work_id = "nonexistent-id"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.single.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=None))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works.validate_uuid", return_value=None),
        ):
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

    @pytest.mark.asyncio
    async def test_create_simple_work_success(self):
        """Test successful creation of a simple work."""
        work_data = MagicMock(spec=WorkCreate)
        work_data.title = "Simple Work"
        work_data.validate = MagicMock(return_value=None)
        work_data.versions = []
        work_data.credits = []
        work_data.genre_ids = []

        mock_supabase = MagicMock()
        works_table = MagicMock()
        works_table.insert.return_value = works_table
        works_table.execute = AsyncMock(return_value=MagicMock(data=[{"work_id": "work-uuid"}]))
        mock_supabase.table.return_value = works_table

        mock_work = MagicMock()
        mock_work.id = "work-uuid"

        expected_payload = work_data.model_dump(exclude_none=True, exclude={"genre_ids", "versions", "credits"})

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse", return_value=mock_work) as mock_parse,
            patch("music_catalogue.crud.works._parse_list", return_value=[]) as mock_parse_list,
            patch("music_catalogue.crud.works.validate_uuid", return_value=None),
            patch("music_catalogue.crud.works.get_by_id", return_value=mock_work),
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await works.create(work_data)

            assert result is mock_work
            mock_get_supabase.assert_awaited_once()
            mock_supabase.table.assert_called_once_with("works")
            works_table.insert.assert_called_once_with(expected_payload)
            work_data.validate.assert_called_once()
            mock_parse.assert_called_once_with(Work, {"work_id": "work-uuid"})
            mock_parse_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_nested_work_success(self):
        """Test successful creation of a complex work with nested relationships."""
        work_data = MagicMock(spec=WorkCreate)
        work_data.title = "Nested Work"
        work_data.validate = MagicMock(return_value=None)
        work_data.versions = [MagicMock(spec=WorkVersionCreate)]
        work_data.credits = [MagicMock(spec=WorkCreditCreate)]
        work_data.genre_ids = ["genre-1"]

        mock_supabase = MagicMock()

        # Mock for works table insert
        works_insert_builder = MagicMock()
        works_insert_builder.execute = AsyncMock(return_value=MagicMock(data=[{"work_id": "work-uuid"}]))
        works_table = MagicMock()
        works_table.insert.return_value = works_insert_builder

        # Mock for versions table insert
        versions_insert_builder = MagicMock()
        versions_insert_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        versions_table = MagicMock()
        versions_table.insert.return_value = versions_insert_builder

        # Mock for credits table insert
        credits_insert_builder = MagicMock()
        credits_insert_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        credits_table = MagicMock()
        credits_table.insert.return_value = credits_insert_builder

        # Mock for work_genres table insert
        work_genres_insert_builder = MagicMock()
        work_genres_insert_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        work_genres_table = MagicMock()
        work_genres_table.insert.return_value = work_genres_insert_builder

        # Mock for get_by_id query
        get_by_id_builder = MagicMock()
        get_by_id_builder.select.return_value = get_by_id_builder
        get_by_id_builder.eq.return_value = get_by_id_builder
        get_by_id_builder.single.return_value = get_by_id_builder
        get_by_id_builder.execute = AsyncMock(
            return_value=MagicMock(data={"work_id": "work-uuid", "title": "Nested Work"})
        )

        # Set up table() to return appropriate mock based on table name
        def table_side_effect(name):
            if name == "works":
                return works_table if mock_supabase.table.call_count == 1 else get_by_id_builder
            elif name == "versions":
                return versions_table
            elif name == "credits":
                return credits_table
            elif name == "work_genres":
                return work_genres_table
            return MagicMock()

        mock_supabase.table.side_effect = table_side_effect

        mock_work = MagicMock()
        mock_work.id = "work-uuid"

        mock_final_work = MagicMock(spec=Work)

        expected_payload = work_data.model_dump(exclude_none=True, exclude={"genre_ids", "versions", "credits"})

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.works._parse") as mock_parse,
            patch("music_catalogue.crud.works.validate_uuid", return_value=None),
            patch("music_catalogue.crud.works.get_by_id", return_value=mock_final_work),
        ):
            mock_get_supabase.return_value = mock_supabase
            mock_parse.side_effect = [mock_work, mock_final_work]

            result = await works.create(work_data)

            assert result is mock_final_work
            mock_get_supabase.assert_awaited_once()
            work_data.validate.assert_called_once()
            works_table.insert.assert_called_once_with(expected_payload)

    @pytest.mark.asyncio
    async def test_create_work_validation_error(self):
        """Test validation errors propagate during work creation."""
        work_data = MagicMock(spec=WorkCreate)
        work_data.validate = MagicMock()
        work_data.validate.side_effect = ValidationError("Test validation error")

        mock_supabase = MagicMock()

        with (
            patch("music_catalogue.crud.works.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
        ):
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(ValidationError) as exc_info:
                await works.create(work_data)

            assert "Test validation error" in str(exc_info.value)
            mock_supabase.table.assert_not_called()
