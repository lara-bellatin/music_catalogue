from typing import List, Optional, Union

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from music_catalogue.crud import artists, unified_search, works
from music_catalogue.models import Artist, EntityType, Person, UnifiedSearchResult, Work

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Unified Search
@app.get("/search", tags=["Unified Search"], response_model=List[UnifiedSearchResult])
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
@app.get("/works/{id}", tags=["Works"], response_model=Work)
async def get_work_by_id(id: str):
    """
    Gets a work by its internal ID.
    """
    return await works.get_by_id(id)


@app.get("/works", tags=["Works"], response_model=List[Work])
async def search_works(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for works based on a query string.
    """
    return await works.search(query)


# Artists
@app.get("/artists/{id}", tags=["Artists"], response_model=Artist)
async def get_artist_by_id(id: str):
    """
    Gets an artist by its internal ID.
    """
    return await artists.get_by_id(id)


@app.get("/artists", tags=["Artists"], response_model=List[Union[Artist, Person]])
async def search_artists(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for artists based on a query string.
    """
    return await artists.search(query)
