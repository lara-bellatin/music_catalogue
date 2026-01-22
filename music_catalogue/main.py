from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from music_catalogue.crud import unified_search
from music_catalogue.models.utils import EntityType, UnifiedSearchResult
from music_catalogue.routers import artists, persons, works

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artists.router)
app.include_router(persons.router)
app.include_router(works.router)


# Unified Search
@app.get("/search", tags=["Unified Search"], response_model=List[UnifiedSearchResult], response_model_exclude_none=True)
async def search_all(
    query: str = Query(min_length=2, max_length=50),
    entity_types: Optional[List[EntityType]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Searches among all entities according to query. Optionally, entities to search among can be limited.
    """
    return await unified_search(query, entity_types or [], limit)
