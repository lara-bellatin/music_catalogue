from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.crud import artists
from music_catalogue.models.artists import Artist, ArtistCreate
from music_catalogue.models.exceptions import APIError, ValidationError

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get("/{id}", response_model=Artist, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_artist_by_id(id: str):
    """
    Gets an artist by its internal ID.
    """
    try:
        return await artists.get_by_id(id)
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to get artist by ID: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Artist], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_artists(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for artists based on a query string.
    """
    try:
        return await artists.search(query)
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to search artists: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=Artist, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_artist(artist_data: ArtistCreate):
    """
    Creates a new artist with nested relationships
    """
    try:
        return await artists.create(artist_data)
    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create artist: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
