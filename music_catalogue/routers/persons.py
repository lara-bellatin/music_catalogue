from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from music_catalogue.crud import persons
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.person_create import PersonCreate
from music_catalogue.models.responses.persons import Person

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.get("/{id}", response_model=Person, response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def get_person_by_id(id: str):
    """
    Gets a person by its internal ID.
    """
    try:
        person = await persons.get_by_id(id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No person found with ID {str(id)}")
        return person
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get person by ID: {str(e)}"
        )
    except:
        raise


@router.get("/", response_model=List[Person], response_model_exclude_none=True, status_code=status.HTTP_200_OK)
async def search_person(query: str = Query(min_length=2, max_length=50)):
    """
    Searches for persons based on a query string.
    """
    try:
        return await persons.search(query)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to search for person: {str(e)}"
        )
    except:
        raise


@router.post("/", response_model=Person, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def create_person(person_data: PersonCreate):
    """
    Creates a new person
    """
    try:
        return await persons.create(person_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create person: {str(e)}"
        )
    except:
        raise


@router.post(
    "/bulk", response_model=List[Person], response_model_exclude_none=True, status_code=status.HTTP_201_CREATED
)
async def bulk_create_persons(people_data: List[PersonCreate]):
    """
    Bulk creates a list of people
    """
    try:
        return [await persons.create(person_data) for person_data in people_data]
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create people in bulk: {str(e)}"
        )
    except:
        raise
