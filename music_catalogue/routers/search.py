from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.crud.search import unified_search
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.search import UnifiedSearchResult
from music_catalogue.models.types import EntityType

router = APIRouter(prefix="/search", tags=["Unified Search"])


# Unified Search
@router.get(
    "/",
    tags=["Unified Search"],
    response_model=List[UnifiedSearchResult],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def search_all(
    query: str = Query(min_length=2, max_length=50),
    entity_types: Optional[List[EntityType]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Searches among all entities according to query. Optionally, entities to search among can be limited.
    """
    try:
        return await unified_search(query, entity_types or [], limit)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search across entities: {str(e)}"
        )
