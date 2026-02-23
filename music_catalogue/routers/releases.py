from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.release_create import ReleaseCreate
from music_catalogue.models.responses.references import ReleaseRef
from music_catalogue.models.responses.releases import Release

router = APIRouter(prefix="/releases", tags=["Releases"])


@router.get("/{id}", response_model=Release, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_release_by_id(id: str):
    """
    Gets a release by its internal ID.
    """
    try:
        release = await Release.get_by_id(id)
        if not release:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No release found with ID {str(id)}")
        return release
    except APIError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get release by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[ReleaseRef], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_releases(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for releases based on a query string.
    """
    try:
        return await Release.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search for release: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Release, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_release(release_data: ReleaseCreate):
    """
    Creates a new release with nested media items and tracks.
    """
    try:
        return await Release.create(release_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create release: {str(e)}"
        )
    except:
        raise
