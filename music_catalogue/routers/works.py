from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.crud import works
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.work_create import WorkCreate
from music_catalogue.models.responses.works import Work

router = APIRouter(prefix="/works", tags=["Works"])


@router.get("/{id}", response_model=Work, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_work_by_id(id: str):
    """
    Gets a work by its internal ID.
    """
    try:
        work = await works.get_by_id(id)
        if not work:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No work found with ID {str(id)}")
        return work
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get work by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[Work], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_works(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for works based on a query string.
    """
    try:
        return await works.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search for work: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Work, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_work(work_data: WorkCreate):
    """
    Creates a new work with nested relationships
    """
    try:
        return await works.create(work_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create work: {str(e)}"
        )
    except:
        raise
