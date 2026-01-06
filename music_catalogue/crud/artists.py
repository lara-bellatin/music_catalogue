from typing import List, Optional, Union

from music_catalogue.crud.supabase_client import get_supabase

from music_catalogue.models.artists import Artist, Person

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
    return Artist.from_dict(res.data[0])

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

    artists = [Artist.from_dict(artist) for artist in artist_data.data]

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
    
    persons = [Person.from_dict(person) for person in person_data.data]

    # TODO: error control
    return artists + persons