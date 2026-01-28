from typing import Dict, List

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.types import EntityType
from music_catalogue.models.validation import validate_uuid
from supabase import PostgrestAPIError


async def get_external_links_raw(entity_type: EntityType, entity_id: str) -> List[Dict[str, any]]:
    """
    Get all external links for an entity and returns the raw data, without parsing

    Args:
        entity_type (EntityType): The type of entity to recover external links for
        entity_id (str): The UUID of the entity to retrieve for

    Returns:
        List[Dict[str, Any]]: The external links found for the entity

    Raises:
        ValidationError: If the UUID format is invalid
        APIError: If Supabase throws an error
    """

    try:
        validate_uuid(entity_id)
        supabase = await get_supabase()
        res = await (
            supabase.table("external_links")
            .select(
                """
                    link_id,
                    label,
                    url,
                    source_verified
                """
            )
            .eq("entity_type", entity_type.value)
            .eq("entity_id", entity_id)
            .execute()
        )

        return res.data

    except PostgrestAPIError as e:
        if e.code == "PGRST116":
            return None
        raise APIError(str(e)) from None
    except Exception as e:
        raise e
