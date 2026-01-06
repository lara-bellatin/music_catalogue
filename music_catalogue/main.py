from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

import music_catalogue.crud.works as works
import music_catalogue.crud.artists as artists

from typing import List, Union
from music_catalogue.models.works import Work
from music_catalogue.models.artists import Artist, Person

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Works
@app.get("/works/{id}", tags=["Works"], response_model=Work)
async def get_work_by_id(id: str):
    """
    Gets a work by its internal ID.
    """
    return await works.get_by_id(id)

@app.get("/works", tags=["Works"], response_model=List[Work])
async def search_works(query: str = Query(None, min_length=2, max_length=50)):
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
async def search_artists(query: str = Query(None, min_length=2, max_length=50)):
    """
    Searches for artists based on a query string.
    """
    return await artists.search(query)
