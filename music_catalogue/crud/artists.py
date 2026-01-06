from typing import List, Optional, Union

from music_catalogue.crud.supabase_client import get_supabase

from music_catalogue.models import Artist, Person, _parse, _parse_list

async def get_by_id(id: str) -> Artist:
    supabase = await get_supabase()
    res = await (
        supabase
        .table("artists")
        .select(
        """
            *,
            artist_memberships(*, person:persons(*)),
            credits(*, works(*), versions(*))
        """
        )
        .eq("artist_id", id)
        .execute()
    )
    
    # TODO: error control
    return _parse(Artist, res.data[0])

async def search(query: str) -> Optional[List[Union[Artist, Person]]]:
    supabase = await get_supabase()
    artist_data = await (
        supabase
        .table("artists")
        .select(
        """
            *,
            person:persons(*),
            artist_memberships(*, person:persons(*)),
            credits(*, works(*), versions(*))
        """
        ).text_search("search_text", query.replace(' ', "+"))
        .execute()
    )

    artists = _parse_list(Artist, artist_data.data)

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

    persons = _parse_list(Person, person_data.data)

    # TODO: error control
    return artists + persons