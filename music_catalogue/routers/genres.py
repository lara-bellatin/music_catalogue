from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.genre_create import GenreCreate
from music_catalogue.models.responses.genres import Genre

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get("/{id}", response_model=Genre, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_genre_by_id(id: str):
    """
    Gets a genre by its internal ID.
    """
    try:
        genre = await Genre.get_by_id(id)
        if not genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No genre found with ID {str(id)}")
        return genre
    except APIError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get genre by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[Genre], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_genres(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for genres based on a query string.
    """
    try:
        return await Genre.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search for genre: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Genre, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_genre(genre_data: GenreCreate):
    """
    Creates a new genre.
    """
    try:
        return await Genre.create(genre_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create genre: {str(e)}"
        )
    except:
        raise
