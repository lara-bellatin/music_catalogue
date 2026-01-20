from typing import List, Optional

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.crud.utils import validate_start_and_end_dates, validate_uuid
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.persons import Person, PersonCreate
from music_catalogue.models.utils import _parse, _parse_list
from supabase import PostgrestAPIError


async def get_by_id(id: str) -> Optional[Person]:
    """
    Get a person by its UUID

    Args:
        id (str): The UUID of the person to retrieve

    Returns:
        Optional[Person]: The person the ID belongs to, if it exists

    Raises:
        ValidationError: If the UUID format is invalid
        APIError: If Supabase throws an error
    """
    try:
        # Check UUID format and raise if invalid
        validate_uuid(id)

        supabase = await get_supabase()
        res = await supabase.table("persons").select("*").eq("person_id", id).single().execute()

        return _parse(Person, res.data)
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def search(query: str) -> List[Person]:
    """
    Search for a person based on a text query

    Args:
        query (str): A query to search for persons by

    Returns:
        List[Person]: A list of persons matching the query

    Raises:
        APIError: If Supabase throws an error
    """
    try:
        supabase = await get_supabase()
        person_data = await (
            supabase.table("persons").select("*").text_search("search_text", query.replace(" ", "+")).execute()
        )

        return _parse_list(Person, person_data.data)
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def create(person_data: PersonCreate) -> Person:
    """
    Creates a new person record

    Args:
        person_data (PersonCreate): The raw data for the person record

    Raises:
        ValidationError: If the input data is invalid
        APIError: If Supabase throws an error
    """
    try:
        # Validate birth and death date if included
        if person_data.birth_date and person_data.death_date:
            validate_start_and_end_dates(person_data.birth_date, person_data.death_date)

        supabase = await get_supabase()
        res = await supabase.table("persons").insert(person_data.model_dump(exclude_none=True)).execute()

        return _parse(Person, res.data[0])
    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e
