from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from music_catalogue.crud import unified_search, works
from music_catalogue.models.utils import EntityType, UnifiedSearchResult
from music_catalogue.models.works import Work
from music_catalogue.routers import artists, persons

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


# Works
@app.get("/works/{id}", tags=["Works"], response_model=Work, response_model_exclude_none=True)
async def get_work_by_id(id: str):
    """
    Gets a work by its internal ID.
    """
    return await works.get_by_id(id)


@app.get("/works", tags=["Works"], response_model=List[Work], response_model_exclude_none=True)
async def search_works(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for works based on a query string.
    """
    return await works.search(query)
