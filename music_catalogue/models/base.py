from typing import TYPE_CHECKING, ClassVar, Dict, List, Optional, Self

from pydantic import BaseModel

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.types import EntityType
from music_catalogue.models.validation import validate_uuid
from supabase import PostgrestAPIError

if TYPE_CHECKING:
    from music_catalogue.models.responses.assets import ExternalLink


class CatalogueModel(BaseModel):
    """
    Base model for all catalogue entities with common CRUD operations.

    Subclasses should define:
        - table_name: The Supabase table name
        - pk_column: The primary key column name (e.g., "work_id")
        - query: The select query string for get_by_id
        - search_query: The select query string for search (optional, defaults to query)
        - search_column: The column to use for text search (optional, defaults to "search_text")
        - entity_type: The EntityType for fetching external links (optional)
        - from_dict: Classmethod to parse a dict into the model
    """

    table_name: ClassVar[str]
    pk_column: ClassVar[str]
    query: ClassVar[str]
    search_query: ClassVar[Optional[str]] = None
    search_column: ClassVar[str] = "search_text"
    entity_type: ClassVar[Optional[EntityType]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        """Parse a dictionary from Supabase into this model. Must be implemented by subclasses."""
        raise NotImplementedError(f"{cls.__name__} must implement from_dict")

    @classmethod
    async def _get_external_links(cls, entity_id: str) -> List["ExternalLink"]:
        """Fetch external links for this entity."""
        from music_catalogue.crud import assets

        return await assets.get_external_links(cls.entity_type, entity_id)

    @classmethod
    async def get_by_id(cls, id: str) -> Optional[Self]:
        """
        Get a record by its UUID.

        Args:
            id: The UUID of the record to retrieve

        Returns:
            The model instance if found, None otherwise

        Raises:
            ValueError: If the UUID format is invalid
            APIError: If Supabase throws an error
        """
        try:
            validate_uuid(id)

            supabase = await get_supabase()
            res = await supabase.table(cls.table_name).select(cls.query).eq(cls.pk_column, id).single().execute()

            if not res.data:
                return None

            instance = cls.from_dict(res.data)

            # Fetch external links if entity_type is defined
            if cls.entity_type and hasattr(instance, "external_links"):
                instance.external_links = await cls._get_external_links(instance.id)

            return instance

        except PostgrestAPIError as e:
            if e.code == "PGRST116":  # Not found
                return None
            raise APIError(str(e)) from None

    @classmethod
    async def search(cls, query: str) -> List[Self]:
        """
        Search for records using text search.

        Args:
            query: The search query string

        Returns:
            List of matching model instances

        Raises:
            APIError: If Supabase throws an error
        """
        try:
            supabase = await get_supabase()
            select_query = cls.search_query or cls.query

            res = await (
                supabase.table(cls.table_name)
                .select(select_query)
                .text_search(cls.search_column, query.replace(" ", "+"))
                .execute()
            )

            return [cls.from_dict(item) for item in res.data] if res.data else []

        except PostgrestAPIError as e:
            raise APIError(str(e)) from None

    @classmethod
    async def create(cls, data: BaseModel, exclude: set = None) -> Self:
        """
        Create a new record.

        Args:
            data: A Pydantic model with the data to insert
            exclude: Fields to exclude from the insert (in addition to None values)

        Returns:
            The created model instance (fetched via get_by_id for complete data)

        Raises:
            APIError: If Supabase throws an error
        """
        try:
            supabase = await get_supabase()
            exclude = exclude or set()

            res = await (
                supabase.table(cls.table_name).insert(data.model_dump(exclude_none=True, exclude=exclude)).execute()
            )

            if not res.data or not res.data[0].get(cls.pk_column):
                raise APIError(f"Unexpected error creating {cls.__name__}. No ID returned")

            return await cls.get_by_id(res.data[0][cls.pk_column])

        except PostgrestAPIError as e:
            raise APIError(str(e)) from None
