from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.search import UnifiedSearchResult
from music_catalogue.models.types import EntityType
from music_catalogue.models.utils import _parse_list
from supabase import PostgrestAPIError


async def unified_search(
    query: str, entity_types: Optional[List[EntityType]] = None, limit: Optional[int] = 20
) -> List[UnifiedSearchResult]:
    """
    Perform search across entities based on a query

    Args:
        query (str): The text query to search by
        entity_types (List[EntityType], optional): A list of entity types to search among. Defaults to include all
        limit (int, optional): The maximum number of results the query should return

    Returns:
        List[UnifiedSearchResult]: A list of results across entities

    Raises:
        APIError: If Supabase throws an error
    """
    try:
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
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e
