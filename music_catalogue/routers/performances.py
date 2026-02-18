from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.performance_create import PerformanceCreate
from music_catalogue.models.responses.performances import Performance, PerformanceRef

router = APIRouter(prefix="/performances", tags=["Performances"])


@router.get("/{id}", response_model=Performance, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_performance_by_id(id: str):
    """
    Gets a performance by its internal ID.
    """
    try:
        performance = await Performance.get_by_id(id)
        if not performance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No performance found with ID {str(id)}")
        return performance
    except APIError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get performance by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[PerformanceRef], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_performances(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for performances based on a query string.
    """
    try:
        return await Performance.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search for performance: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Performance, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_performance(performance_data: PerformanceCreate):
    """
    Creates a new performance with nested artists and works.
    """
    try:
        return await Performance.create(performance_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create performance: {str(e)}"
        )
    except:
        raise
