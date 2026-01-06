from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models import EntityType, UnifiedSearchResult, _parse_list


async def unified_search(
    query: str, entity_types: Optional[List[EntityType]] = None, limit: Optional[int] = 20
) -> List[UnifiedSearchResult]:
    supabase = await get_supabase()
    search_query = supabase.rpc(
        "unified_search",
        {
            "query_text": query.replace(" ", "+"),
            "fetch_limit": limit,
        },
    ).select("*")

    if entity_types:
        query = search_query.in_("entity_type", entity_types)

    res = await search_query.execute()

    return _parse_list(UnifiedSearchResult, res.data)
