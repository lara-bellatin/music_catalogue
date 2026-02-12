from typing import List

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.types import EntityType
from music_catalogue.models.utils import _parse_list
from music_catalogue.models.validation import validate_uuid
from supabase import PostgrestAPIError


async def get_external_links(entity_type: EntityType, entity_id: str) -> List[ExternalLink]:
    """
    Get all external links for an entity

    Args:
        entity_type (EntityType): The type of entity to recover external links for
        entity_id (str): The UUID of the entity to retrieve for

    Returns:
        List[ExternalLink]: The external links found for the entity

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

        return _parse_list(ExternalLink, res.data)

    except PostgrestAPIError as e:
        if e.code == "PGRST116":
            return None
        raise APIError(str(e)) from None
    except Exception as e:
        raise e


async def bulk_create_external_links(
    data: ExternalLinkCreate, entity_type: EntityType, entity_id: str
) -> List[ExternalLink]:
    """
    Bulk creates external links for a specified entity

    Args:
        data (ExternalLinkCreate): Payload to use to create external links
        entity_type (EntityType): The type for the entity the links belong to
        entity_id (str): The ID of the entity the links belong to

    Returns:
        List[ExternalLink]: A list of the created external links

    Raises:
        APIError: If Supabase throws an error
    """
    supabase = await get_supabase()

    try:
        external_links = await (
            supabase.table("external_links")
            .insert(
                [
                    {
                        "entity_type": entity_type.value,
                        "entity_id": entity_id,
                        **link.model_dump(exclude_none=True),
                        # TODO: Remove hardcoded value once user implementation is done
                        "added_by": "760c6a23-cf19-4e59-89aa-f6921943bc26",
                    }
                    for link in data.external_links
                ]
            )
            .execute()
        )

        return _parse_list(external_links.data)

    except PostgrestAPIError as e:
        raise APIError(str(e)) from None
    except Exception as e:
        raise e
