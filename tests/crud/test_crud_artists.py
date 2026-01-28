"""
Unit tests for CRUD operations on artists CRUD module.
"""

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from music_catalogue.crud import artists
from music_catalogue.models.inputs.artist_create import ArtistCreate, ArtistMembershipCreate, ArtistType
from music_catalogue.models.responses.artists import Artist


class TestArtistsCRUD:
    """Tests for artists CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_artist_by_id_success(self):
        """Test successfully retrieving an artist by ID."""
        artist_id = "artist-1"
        mock_artist_data = {
            "artist_id": artist_id,
            "display_name": "Carl Nielsen",
            "artist_type": "solo",
        }

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.single.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_artist_data))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse", return_value=MagicMock(spec=Artist)) as mock_parse,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None) as mock_validate_uuid,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.get_by_id(artist_id)

            assert result is mock_parse.return_value
            mock_validate_uuid.assert_called_once_with(artist_id)
            mock_supabase.table.assert_called_once_with("artists")
            mock_parse.assert_called_once_with(Artist, mock_artist_data)

    @pytest.mark.asyncio
    async def test_get_artist_by_id_not_found(self):
        """Test retrieving an artist that doesn't exist."""
        artist_id = "nonexistent-artist"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.eq.return_value = query_builder
        query_builder.single.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.get_by_id(artist_id)
            assert result is None

    @pytest.mark.asyncio
    async def test_search_artists_success(self):
        """Test searching for artists with a valid query."""
        query = "nielsen"
        mock_results = [
            {"artist_id": "id1", "display_name": "Carl Nielsen", "artist_type": "solo"},
        ]

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=mock_results))
        mock_supabase.table.return_value = query_builder

        parsed_artists = [MagicMock(spec=Artist) for _ in mock_results]

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch(
                "music_catalogue.crud.artists._parse_list",
                return_value=parsed_artists,
            ) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.search(query)

            assert result is parsed_artists
            mock_parse_list.assert_called_once_with(Artist, mock_results)
            query_builder.text_search.assert_called_once_with("search_text", query.replace(" ", "+"))

    @pytest.mark.asyncio
    async def test_search_artists_empty_results(self):
        """Test searching for artists with no matches."""
        query = "fakename"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse_list", return_value=[]) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.search(query)

            assert result == []
            mock_parse_list.assert_called_once_with(Artist, [])

    @pytest.mark.asyncio
    async def test_search_artists_query_normalization(self):
        """Test that search query spaces are normalized to +."""
        query = "carl nielsen"

        mock_supabase = MagicMock()
        query_builder = MagicMock()
        query_builder.select.return_value = query_builder
        query_builder.text_search.return_value = query_builder
        query_builder.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase.table.return_value = query_builder

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse_list", return_value=[]),
        ):
            mock_get_supabase.return_value = mock_supabase

            await artists.search(query)

            query_builder.text_search.assert_called_once_with("search_text", "carl+nielsen")

    @pytest.mark.asyncio
    async def test_create_artist_solo_success(self):
        """Test successful creation of a SOLO artist."""
        artist_data = MagicMock(spec=ArtistCreate)
        artist_data.artist_type = ArtistType.SOLO
        artist_data.display_name = "Solo artist"
        artist_data.person_id = "person-123"
        artist_data.members = []

        mock_supabase = MagicMock()
        artists_table = MagicMock()
        artists_table.insert.return_value = artists_table
        artists_table.execute = AsyncMock(return_value=MagicMock(data=[{"artist_id": "artist-uuid"}]))
        mock_supabase.table.return_value = artists_table

        mock_artist = MagicMock()
        mock_artist.id = "artist-uuid"

        expected_payload = artist_data.model_dump(exclude_none=True, exclude={"members"})

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse", return_value=mock_artist) as mock_parse,
            patch("music_catalogue.crud.artists._parse_list", return_value=[]) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.create(artist_data)

            assert result is mock_artist
            mock_get_supabase.assert_awaited_once()
            mock_supabase.table.assert_called_once_with("artists")
            artists_table.insert.assert_called_once_with(expected_payload)
            mock_parse.assert_called_once_with(Artist, {"artist_id": "artist-uuid"})
            mock_parse_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_artist_group_success(self):
        """Test successful creation of a GROUP artist with memberships."""
        artist_membership_data = MagicMock(spec=ArtistMembershipCreate)
        artist_membership_data.person_id = "person-1"
        artist_membership_data.start_year = 1985
        artist_membership_data.end_year = 1988

        artist_data = MagicMock(spec=ArtistCreate)
        artist_data.artist_type = ArtistType.GROUP
        artist_data.display_name = "The Ensemble"
        artist_data.start_year = 1980
        artist_data.end_year = 1990
        artist_data.members = [artist_membership_data]

        mock_supabase = MagicMock()
        artists_table = MagicMock()
        artists_table.insert.return_value = artists_table
        artists_table.execute = AsyncMock(return_value=MagicMock(data=[{"artist_id": "group-123"}]))
        memberships_table = MagicMock()
        memberships_table.insert.return_value = memberships_table
        memberships_table.execute = AsyncMock(return_value=MagicMock(data=[{"membership_id": "mem-1"}]))

        table_map = {"artists": artists_table, "artist_memberships": memberships_table}
        mock_supabase.table.side_effect = lambda name: table_map[name]

        mock_artist = MagicMock()
        mock_artist.id = "group-123"
        mock_artist.members = []

        parsed_memberships = [MagicMock()]

        expected_artist_payload = artist_data.model_dump(exclude_none=True, exclude={"members"})
        expected_members_payload = [
            {"group_id": "group-123", **member.model_dump(exclude_none=True)} for member in artist_data.members
        ]

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists._parse", return_value=mock_artist) as mock_parse,
            patch("music_catalogue.crud.artists._parse_list", return_value=parsed_memberships) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.create(artist_data)

            assert result is mock_artist
            assert result.members is parsed_memberships
            mock_supabase.table.assert_has_calls([call("artists"), call("artist_memberships")])
            artists_table.insert.assert_called_once_with(expected_artist_payload)
            memberships_table.insert.assert_called_once_with(expected_members_payload)
            mock_parse.assert_called_once_with(Artist, {"artist_id": "group-123"})
            mock_parse_list.assert_called_once()
