from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.artists import Artist, ArtistCreate, ArtistMembership
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.utils import _parse, _parse_list, validate_uuid
from supabase import PostgrestAPIError


async def get_by_id(id: str) -> Optional[Artist]:
    """
    Get an artist by its UUID

    Args:
        id (str): The UUID of the artist to retrieve

    Returns:
        Optional[Artist]: The artist the ID belongs to, if it exists

    Raises:
        ValidationError: If the UUID format is invalid
        APIError: If Supabase throws an error
    """
    try:
        # Check UUID format and raise if invalid
        validate_uuid(id)

        supabase = await get_supabase()
        res = await (
            supabase.table("artists")
            .select(
                """
                *,
                artist_memberships(*, person:persons(*)),
                credits(*, works(*), versions(*))
            """
            )
            .eq("artist_id", id)
            .single()
            .execute()
        )

        return _parse(Artist, res.data)
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def search(query: str) -> List[Artist]:
    """
    Search for an artist based on a text query

    Args:
        query (str): A query to search for artists by

    Returns:
        List[Artist]: A list of artists matching the query

    Raises:
        APIError: If Supabase throws an error
    """
    try:
        supabase = await get_supabase()
        artist_data = await (
            supabase.table("artists")
            .select(
                """
                *,
                person:persons(*),
                artist_memberships(*, person:persons(*)),
                credits(*, works(*), versions(*))
            """
            )
            .text_search("search_text", query.replace(" ", "+"))
            .execute()
        )

        return _parse_list(Artist, artist_data.data)
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def create(artist_data: ArtistCreate) -> Artist:
    """
    Create a new artist record and its optional nested members

    Args:
        artist_data (ArtistCreate): The raw data for the artist and optional members

    Returns:
        Artist: An artist object representing the new record created

    Raises:
        ValidationError: If the input data is invalid
        APIError: If Supabase throws an error
    """
    try:
        # Validate artist data is complete
        artist_data.validate()

        supabase = await get_supabase()

        # Create artist
        res = await (
            supabase.table("artists").insert(artist_data.model_dump(exclude_none=True, exclude={"members"})).execute()
        )

        artist = _parse(Artist, res.data[0])

        if not artist.id:
            raise APIError("Unexpected error creating artist. No ID returned")

        # Create memberships
        if artist_data.members:
            members_res = await (
                supabase.table("artist_memberships")
                .insert(
                    [{"group_id": artist.id, **member.model_dump(exclude_none=True)} for member in artist_data.members]
                )
                .execute()
            )

            memberships = _parse_list(ArtistMembership, members_res.data)
            artist.members = memberships

        return artist
    except PostgrestAPIError as e:
        # Roll back artist creation if member creation fails
        if artist and artist.id:
            await supabase.table("artists").delete().eq("artist_id", artist.id).execute()
        raise APIError(str(e)) from None
    except Exception as e:
        raise e
