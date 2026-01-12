"""
Unit tests for CRUD operations on artists CRUD module.
"""

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from music_catalogue.crud import artists
from music_catalogue.models.artists import Artist, Person


class TestArtistsCRUD:
    """Tests for artists CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_artist_by_id_success(self):
        """Test successfully retrieving an artist by ID."""
        artist_id = "456f5678-f89c-12d3-b567-526725285001"
        mock_artist_data = {
            "artist_id": artist_id,
            "display_name": "Carl Nielsen",
            "artist_type": "solo",
        }

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[mock_artist_data]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse", return_value=MagicMock(spec=Artist)) as mock_parse,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.get_by_id(artist_id)

            assert result is mock_parse.return_value
            mock_parse.assert_called_once_with(Artist, mock_artist_data)
            mock_supabase.table.assert_called_once_with("artists")

    @pytest.mark.asyncio
    async def test_get_artist_by_id_not_found(self):
        """Test retrieving an artist that doesn't exist."""
        artist_id = "nonexistent-artist"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase:
            mock_get_supabase.return_value = mock_supabase

            result = await artists.get_by_id(artist_id)
            assert result is None

    @pytest.mark.asyncio
    async def test_search_artists_success(self):
        """Test searching for artists with a valid query."""
        query = "nielsen"
        mock_artist_rows = [
            {"artist_id": "id1", "display_name": "Carl Nielsen", "artist_type": "solo"},
        ]
        mock_person_rows = [
            {"person_id": "p1", "legal_name": "Carl Nielsen"},
        ]

        mock_supabase = MagicMock()
        artist_query = MagicMock()
        artist_query.select.return_value = artist_query
        artist_query.text_search.return_value = artist_query
        artist_query.execute = AsyncMock(return_value=MagicMock(data=mock_artist_rows))

        person_query = MagicMock()
        person_query.select.return_value = person_query
        person_query.text_search.return_value = person_query
        person_query.execute = AsyncMock(return_value=MagicMock(data=mock_person_rows))

        mock_supabase.table.side_effect = {
            "artists": artist_query,
            "persons": person_query,
        }.__getitem__

        mock_artist_objects = [MagicMock(spec=Artist)]
        mock_person_objects = [MagicMock(spec=Person)]

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch(
                "music_catalogue.crud.artists._parse_list",
                side_effect=[mock_artist_objects, mock_person_objects],
            ) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.search(query)

            assert result == mock_artist_objects + mock_person_objects
            assert mock_parse_list.call_args_list == [
                call(Artist, mock_artist_rows),
                call(Person, mock_person_rows),
            ]
            assert mock_supabase.table.call_args_list == [call("artists"), call("persons")]

    @pytest.mark.asyncio
    async def test_search_artists_empty_results(self):
        """Test searching for artists with no matches."""
        query = "fakename"

        mock_supabase = MagicMock()
        artist_query = MagicMock()
        artist_query.select.return_value = artist_query
        artist_query.text_search.return_value = artist_query
        artist_query.execute = AsyncMock(return_value=MagicMock(data=[]))

        person_query = MagicMock()
        person_query.select.return_value = person_query
        person_query.text_search.return_value = person_query
        person_query.execute = AsyncMock(return_value=MagicMock(data=[]))

        mock_supabase.table.side_effect = {
            "artists": artist_query,
            "persons": person_query,
        }.__getitem__

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse_list", side_effect=[[], []]) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.search(query)

            assert result == []
            assert mock_parse_list.call_args_list == [
                call(Artist, []),
                call(Person, []),
            ]

    @pytest.mark.asyncio
    async def test_search_artists_query_normalization(self):
        """Test that search query spaces are normalized to +."""
        query = "carl nielsen"

        mock_supabase = MagicMock()
        artist_query = MagicMock()
        artist_query.select.return_value = artist_query
        artist_query.text_search.return_value = artist_query
        artist_query.execute = AsyncMock(return_value=MagicMock(data=[]))

        person_query = MagicMock()
        person_query.select.return_value = person_query
        person_query.text_search.return_value = person_query
        person_query.execute = AsyncMock(return_value=MagicMock(data=[]))

        mock_supabase.table.side_effect = {
            "artists": artist_query,
            "persons": person_query,
        }.__getitem__

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse_list", return_value=[]),
        ):
            mock_get_supabase.return_value = mock_supabase

            await artists.search(query)

            artist_query.text_search.assert_called_once_with("search_text", "carl+nielsen")
            person_query.text_search.assert_called_once_with("search_text", "carl+nielsen")
