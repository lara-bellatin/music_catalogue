from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase

from music_catalogue.models.artists import Artist

async def get_by_id(id: str) -> Artist:
    supabase = await get_supabase()
    res = await (
        supabase
        .table("artists")
        .select(
        """
            *,
            artist_memberships(*, persons(*)),
            versions(
                *,
                versions!based_on_version_id(*),
                release_tracks(*, releases(*)),
                credits(
                    *,
                    persons(*),
                    artists(*, persons(*), artist_memberships(persons(*)))
                )
            ),
            credits(*, works(*), versions(*))
        """
        )
        .eq("artist_id", id)
        .execute()
    )
    
    # TODO: use model validation
    return res.data[0]

async def search(query: str) -> Optional[List[Artist]]:
    supabase = await get_supabase()
    artist_data = await (
        supabase
        .table("artists")
        .select(
        """
            *,
            persons(*),
            artist_memberships(*, persons(*)),
            versions(
                *,
                versions!based_on_version_id(*),
                release_tracks(*, releases(*)),
                credits(
                    *,
                    persons(*),
                    artists(*, persons(*), artist_memberships(persons(*)))
                )
            ),
            credits(*, works(*), versions(*))
        """
        ).text_search("search_text", query.replace(' ', "+"))
        .execute()
    )

    person_data = await (
        supabase
        .table("persons")
        .select(
        """
            *
            artists(*),
            artist_memberships(*, artists(*)),
            credits(*, works(*), versions(*))
        """
        ).text_search("search_text", query.replace(' ', '+'))
        .execute()
    )
    # TODO: add error control
    # TODO: use model validation
    return artist_data.data + person_data.data