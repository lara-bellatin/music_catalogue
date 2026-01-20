"""
Unit tests for CRUD operations on artists CRUD module.
"""

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from music_catalogue.crud import artists
from music_catalogue.models.artists import Artist, ArtistCreate, ArtistMembershipCreate, ArtistType
from music_catalogue.models.exceptions import ValidationError


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
        artist_data = ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="Solo artist",
            person_id="person-123",
        )

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
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None) as mock_validate_uuid,
            patch(
                "music_catalogue.crud.artists.validate_start_and_end_years", return_value=None
            ) as mock_validate_years,
            patch("music_catalogue.crud.artists._parse", return_value=mock_artist) as mock_parse,
            patch("music_catalogue.crud.artists._parse_list", return_value=[]) as mock_parse_list,
        ):
            mock_get_supabase.return_value = mock_supabase

            result = await artists.create(artist_data)

            assert result is mock_artist
            mock_get_supabase.assert_awaited_once()
            mock_supabase.table.assert_called_once_with("artists")
            artists_table.insert.assert_called_once_with(expected_payload)
            mock_validate_uuid.assert_called_once_with("person-123")
            mock_validate_years.assert_not_called()
            mock_parse.assert_called_once_with(Artist, {"artist_id": "artist-uuid"})
            mock_parse_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_artist_group_success(self):
        """Test successful creation of a GROUP artist with memberships."""
        artist_data = ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="The Ensemble",
            start_year=1980,
            end_year=1990,
            members=[
                ArtistMembershipCreate(person_id="person-1", start_year=1985, end_year=1988),
                ArtistMembershipCreate(person_id="person-2"),
            ],
        )

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
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None) as mock_validate_uuid,
            patch(
                "music_catalogue.crud.artists.validate_start_and_end_years", return_value=None
            ) as mock_validate_years,
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
            assert mock_validate_uuid.call_count == len(artist_data.members)
            mock_validate_years.assert_has_calls([call(1985, 1988), call(1980, 1990)])
            mock_parse.assert_called_once_with(Artist, {"artist_id": "group-123"})
            mock_parse_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_artist_solo_missing_person_id_raises(self):
        """Test SOLO artist creation fails when person_id is missing."""
        artist_data = ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="Solo Without Person",
        )

        mock_supabase = MagicMock()

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None) as mock_validate_uuid,
            patch("music_catalogue.crud.artists.validate_start_and_end_years", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(ValidationError) as exc_info:
                await artists.create(artist_data)

            assert "Missing person ID for SOLO type artist" in str(exc_info.value)
            mock_supabase.table.assert_not_called()
            mock_validate_uuid.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_artist_solo_with_members_raises(self):
        """Test SOLO artist creation fails when members are provided."""
        artist_data = ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="Solo With Members",
            person_id="person-abc",
            members=[ArtistMembershipCreate(person_id="member-1")],
        )

        mock_supabase = MagicMock()

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None) as mock_validate_uuid,
            patch("music_catalogue.crud.artists.validate_start_and_end_years", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(ValidationError) as exc_info:
                await artists.create(artist_data)

            assert "There cannot be members for a SOLO type artist" in str(exc_info.value)
            mock_supabase.table.assert_not_called()
            mock_validate_uuid.assert_called_once_with("person-abc")

    @pytest.mark.asyncio
    async def test_create_artist_group_missing_members_raises(self):
        """Test GROUP artist creation fails when members are missing."""
        artist_data = ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="Memberless Group",
        )

        mock_supabase = MagicMock()

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None),
            patch("music_catalogue.crud.artists.validate_start_and_end_years", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(ValidationError) as exc_info:
                await artists.create(artist_data)

            assert "Missing members for GROUP type artist" in str(exc_info.value)
            mock_supabase.table.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_artist_group_with_person_id_raises(self):
        """Test GROUP artist creation fails when person_id is provided."""
        artist_data = ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="Group With Person",
            person_id="person-xyz",
            members=[ArtistMembershipCreate(person_id="member-1")],
        )

        mock_supabase = MagicMock()

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None) as mock_validate_uuid,
            patch("music_catalogue.crud.artists.validate_start_and_end_years", return_value=None),
        ):
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(ValidationError) as exc_info:
                await artists.create(artist_data)

            assert "Invalid assignment of person to GROUP type artist" in str(exc_info.value)
            mock_supabase.table.assert_not_called()
            mock_validate_uuid.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_artist_group_member_validation_error(self):
        """Test GROUP artist creation surfaces nested member validation errors."""
        artist_data = ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="Group With Invalid Member",
            members=[ArtistMembershipCreate(person_id="member-bad", start_year=2000, end_year=1990)],
        )

        mock_supabase = MagicMock()

        with (
            patch("music_catalogue.crud.artists.get_supabase", new_callable=AsyncMock) as mock_get_supabase,
            patch("music_catalogue.crud.artists.validate_uuid", return_value=None),
            patch(
                "music_catalogue.crud.artists.validate_start_and_end_years",
                side_effect=ValidationError("Invalid years"),
            ),
        ):
            mock_get_supabase.return_value = mock_supabase

            with pytest.raises(ValidationError) as exc_info:
                await artists.create(artist_data)

            assert "Invalid member configuration for person with ID member-bad" in str(exc_info.value)
            mock_supabase.table.assert_not_called()
