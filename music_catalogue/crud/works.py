from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase

from music_catalogue.models.works import Work

async def get_by_id(id: str) -> Work:
    supabase = await get_supabase()
    res = await (
        supabase
        .table("works")
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
        .eq("work_id", id)
        .execute()
    )
    
    # TODO: use model validation
    return res.data[0]

async def search(query: str) -> Optional[List[Work]]:
    supabase = await get_supabase()
    data = await (
        supabase
        .table("works")
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
        ).text_search("search_text", query.replace(' ', "+"))
        .execute()
    )
    # TODO: add error control
    # TODO: use model validation
    return data
