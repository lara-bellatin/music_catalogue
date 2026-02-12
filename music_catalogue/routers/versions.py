from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.version_create import VersionCreate
from music_catalogue.models.responses.references import VersionRef
from music_catalogue.models.responses.versions import Version

router = APIRouter(prefix="/versions", tags=["Versions"])


@router.get("/{id}", response_model=Version, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_version_by_id(id: str):
    """
    Gets a version by its internal ID.
    """
    try:
        version = await Version.get_by_id(id)
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No version found with ID {str(id)}")
        return version
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get version by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[VersionRef], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_versions(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for versions based on a query string.
    """
    try:
        return await Version.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search for version: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Version, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_version(version_data: VersionCreate):
    """
    Creates a new version with nested relationships
    """
    try:
        return await Version.create(version_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create version: {str(e)}"
        )
    except:
        raise
