from typing import ClassVar, Dict, List, Optional, Self

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.types import EntityType
from supabase import PostgrestAPIError


class Genre(CatalogueModel):
    table_name: ClassVar[str] = "genres"
    pk_column: ClassVar[str] = "genre_id"
    entity_type: ClassVar[EntityType] = EntityType.GENRE
    query: ClassVar[str] = "genre_id, name, description"

    id: str
    name: str
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Genre":
        return cls(
            id=data["genre_id"],
            name=data["name"],
            description=data.get("description"),
        )

    @classmethod
    async def search(cls, query: str) -> List[Self]:
        try:
            supabase = await get_supabase()
            res = await supabase.table(cls.table_name).select(cls.query).ilike("name", f"%{query}%").execute()
            return [cls.from_dict(item) for item in res.data] if res.data else []
        except PostgrestAPIError as e:
            raise APIError(str(e)) from None
