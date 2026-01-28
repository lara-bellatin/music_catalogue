"""
Unit tests for CRUD operations on persons CRUD module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from music_catalogue.crud import persons
from music_catalogue.models.inputs.person_create import PersonCreate
from music_catalogue.models.responses.persons import Person


class TestPersonsCRUD:
    """Tests for persons CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_person_by_id_success(self):
        """Test successfully retrieving an person by ID."""
        person_id = "person-1"
        mock_person_data = {
            "person_id": person_id,
            "legal_name": "Carl Nielsen",
        }

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.single.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_person_data))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.persons.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.persons._parse", return_value=MagicMock(spec=Person)) as mock_parse,
            patch("music_catalogue.crud.persons.validate_uuid", return_value=None) as mock_validate_uuid,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await persons.get_by_id(person_id)

            assert result is mock_parse.return_value
            mock_validate_uuid.assert_called_once_with(person_id)
            mock_supabase.table.assert_called_once_with("persons")
            mock_parse.assert_called_once_with(Person, mock_person_data)

    @pytest.mark.asyncio
    async def test_get_person_by_id_not_found(self):
        """Test retrieving an person that doesn't exist."""
        person_id = "nonexistent-person"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.single.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.persons.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.persons.validate_uuid", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await persons.get_by_id(person_id)
            assert result is None

    @pytest.mark.asyncio
    async def test_search_persons_success(self):
        """Test searching for persons with a valid query."""
        query = "nielsen"
        mock_results = [
            {"person_id": "id1", "legal_name": "Carl Nielsen"},
        ]

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_results))
        mock_supabase.table.return_value = query_builder

        parsed_persons = [MagicMock(spec=Person) for _ in mock_results]

        with (
            patch("music_catalogue.crud.persons.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch(
                "music_catalogue.crud.persons._parse_list",
                return_value=parsed_persons,
            ) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await persons.search(query)

            assert result is parsed_persons
            mock_parse_list.assert_called_once_with(Person, mock_results)
            query_builder.text_search.assert_called_once_with("search_text", query.replace(" ", "+"))

    @pytest.mark.asyncio
    async def test_search_persons_empty_results(self):
        """Test searching for persons with no matches."""
        query = "fakename"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.persons.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.persons._parse_list", return_value=[]) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await persons.search(query)

            assert result == []
            mock_parse_list.assert_called_once_with(Person, [])

    @pytest.mark.asyncio
    async def test_search_persons_query_normalization(self):
        """Test that search query spaces are normalized to +."""
        query = "carl nielsen"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.persons.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.persons._parse_list", return_value=[]),
        ):
            mock_get_supabase.return_value = mock_supabase

            await persons.search(query)

            query_builder.text_search.assert_called_once_with("search_text", "carl+nielsen")

    @pytest.mark.asyncio
    async def test_create_person_success(self):
        """Test creating a person succesfully."""
        person_data = MagicMock(spec=PersonCreate)
        person_data.legal_name = "Carl Nielsen"
        person_data.pronouns = "he/him"
        person_data.validate = MagicMock(return_value=None)

        mock_supabase = MagicMock()
        persons_table = MagicMock()
        persons_table.insert.return_value = persons_table
        persons_table.execute = AsyncMock(return_value=MagicMock(data=[{"person_id": "person-uuid"}]))
        mock_supabase.table.return_value = persons_table

        mock_person = MagicMock(spec=Person)

        expected_payload = person_data.model_dump(exclude_none=True)

        with (
            patch("music_catalogue.crud.persons.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.persons._parse", return_value=mock_person) as mock_parse,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await persons.create(person_data)

            assert result is mock_person
            mock_supabase.table.assert_called_once_with("persons")
            persons_table.insert.assert_called_once_with(expected_payload)
            mock_parse.assert_called_once_with(Person, {"person_id": "person-uuid"})
