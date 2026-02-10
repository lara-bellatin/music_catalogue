from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.artist_create import ArtistCreate
from music_catalogue.models.responses.artists import Artist
from music_catalogue.models.responses.references import ArtistRef

router = APIRouter(prefix="/artists", tags=["Artists"])


@router.get("/{id}", response_model=Artist, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_artist_by_id(id: str):
    """
    Gets an artist by its internal ID.
    """
    try:
        artist = await Artist.get_by_id(id)
        if not artist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No artist found with ID {str(id)}")
        return artist
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get artist by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[ArtistRef], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_artists(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for artists based on a query string.
    """
    try:
        return await Artist.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search artists: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Artist, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_artist(artist_data: ArtistCreate):
    """
    Creates a new artist with nested relationships
    """
    try:
        return await Artist.create(artist_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create artist: {str(e)}"
        )
    except:
        raise
