from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.utils import _parse, _parse_list, validate_uuid
from music_catalogue.models.works import Work, WorkCreate
from supabase import PostgrestAPIError


async def get_by_id(id: str) -> Optional[Work]:
    """
    Get a work by its UUID

    Args:
        id (str): The UUID of the work to retrieve

    Returns:
        Optional[Work]: The work the ID belongs to, if it exists

    Raises:
        ValidationError: If the UUID format is invalid
        APIError: If Supabase throws an error
    """
    try:
        # Check UUID format and raise if invalid
        validate_uuid(id)

        supabase = await get_supabase()
        res = await (
            supabase.table("works")
            .select(
                """
                *,
                versions(
                    *,
                    versions!based_on_version_id(*, artist:artists(*)),
                    artist:artists(*, person:persons(*), artist_memberships(*, person:persons(*))),
                    release_tracks(*, releases(*)),
                    credits(
                        *,
                        person:persons(*),
                        artist:artists(*, person:persons(*), artist_memberships(persons(*)))
                    ),
                    primary_artist:artists!fk_versions_primary_artist(*, person:persons(*), artist_memberships(*, person:persons(*)))
                ),
                work_genres(genres(*)),
                credits(*, person:persons(*), artist:artists(*, artist_memberships(*, person:persons(*))))
            """
            )
            .eq("work_id", id)
            .single()
            .execute()
        )

        return _parse(Work, res.data)
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def search(query: str) -> List[Work]:
    """
    Search for a work based on a text query

    Args:
        query (str): A query to search for works by

    Returns:
        List[Work]: A list of works matching the query

    Raises:
        APIError: If Supabase throws an error
    """
    try:
        supabase = await get_supabase()
        res = await (
            supabase.table("works")
            .select(
                """
                *,
                versions(
                    *,
                    versions!based_on_version_id(*, artists(*)),
                    artists(*, persons(*), artist_memberships(*, persons(*))),
                    release_tracks(*, releases(*)),
                    credits(
                        *,
                        persons(*),
                        artists(*, persons(*), artist_memberships(persons(*)))
                    )
                ),
                work_genres(genres(*)),
                credits(*, persons(*), artists(*, artist_memberships(*, persons(*))))
            """
            )
            .text_search("search_text", query.replace(" ", "+"))
            .execute()
        )

        return _parse_list(Work, res.data)
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def create(work_data: WorkCreate) -> Work:
    """
    Create a new work record and its optional nested relationships

    Args:
        work_data (WorkCreate): The raw data for the work and optional relationships

    Returns:
        Work: A work object representing the new record created

    Raises:
        ValidationError: If the input data is invalid
        APIError: If Supabase throws an error
    """
    try:
        # Validate work data is complete
        work_data.validate()

        supabase = await get_supabase()

        # Create work
        res = await (
            supabase.table("works")
            .insert(work_data.model_dump(exclude_none=True, exclude={"genre_ids", "versions", "credits"}))
            .execute()
        )

        work = _parse(Work, res.data[0])

        if not work.id:
            raise APIError("Unexpected error creating work. No ID returned")

        # Create versions
        if work_data.versions:
            await (
                supabase.table("versions")
                .insert(
                    [{"work_id": work.id, **version.model_dump(exclude_none=True)} for version in work_data.versions]
                )
                .execute()
            )

        # Create credits
        if work_data.credits:
            await (
                supabase.table("credits")
                .insert([{"work_id": work.id, **credit.model_dump(exclude_none=True)} for credit in work_data.credits])
                .execute()
            )

        # Assign genres
        if work_data.genre_ids:
            await (
                supabase.table("work_genres")
                .insert([{"work_id": work.id, "genre_id": genre_id} for genre_id in work_data.genre_ids])
                .execute()
            )

        # Get work by ID to include complete information
        return await get_by_id(work.id)

    except PostgrestAPIError as e:
        # Roll back work creation and its relationships if any relationship creation fails
        if work and work.id:
            await supabase.table("works").delete().eq("work_id", work.id).execute()
            await supabase.table("versions").delete().eq("work_id", work.id).execute()
            await supabase.table("credits").delete().eq("work_id", work.id).execute()
            await supabase.table("work_genres").delete().eq("work_id", work.id).execute()
        raise APIError(str(e)) from None
    except Exception as e:
        raise e
