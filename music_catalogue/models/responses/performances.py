from datetime import date, datetime
from typing import ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.performance_create import PerformanceCreate
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import PerformanceArtistRef, PerformanceRef, PerformanceWorkRef
from music_catalogue.models.types import EntityType
from music_catalogue.models.utils import _parse_list
from supabase import PostgrestAPIError


class Performance(CatalogueModel):
    table_name: ClassVar[str] = "performances"
    pk_column: ClassVar[str] = "performance_id"
    entity_type: ClassVar[EntityType] = EntityType.PERFORMANCE
    ref_model: ClassVar[BaseModel] = PerformanceRef
    query: ClassVar[str] = f"""
        performance_id,
        name,
        performance_date,
        venue,
        city,
        country,
        notes,
        performance_artists({PerformanceArtistRef.query}),
        performance_works({PerformanceWorkRef.query})
    """

    id: str
    name: str
    performance_date: Optional[date] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    artists: List[PerformanceArtistRef] = Field(default_factory=list)
    works: List[PerformanceWorkRef] = Field(default_factory=list)
    external_links: List[ExternalLink] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Performance":
        return cls(
            id=data["performance_id"],
            name=data["name"],
            performance_date=datetime.strptime(data["performance_date"], "%Y-%m-%d").date()
            if data.get("performance_date")
            else None,
            venue=data.get("venue"),
            city=data.get("city"),
            country=data.get("country"),
            notes=data.get("notes"),
            artists=_parse_list(PerformanceArtistRef, data.get("performance_artists")),
            works=_parse_list(PerformanceWorkRef, data.get("performance_works")),
        )

    @classmethod
    async def create(cls, data: "PerformanceCreate", exclude: set = None) -> "Performance":
        exclude = (exclude or set()) | {"artists", "works", "external_links"}
        supabase = await get_supabase()
        performance = None

        try:
            performance = await super().create(data, exclude=exclude)

            if data.artists:
                await (
                    supabase.table("performance_artists")
                    .insert(
                        [
                            {"performance_id": performance.id, **artist.model_dump(exclude_none=True)}
                            for artist in data.artists
                        ]
                    )
                    .execute()
                )

            if data.works:
                await (
                    supabase.table("performance_works")
                    .insert(
                        [
                            {"performance_id": performance.id, **work.model_dump(exclude_none=True)}
                            for work in data.works
                        ]
                    )
                    .execute()
                )

            return await cls.get_by_id(performance.id)

        except PostgrestAPIError as e:
            if performance and performance.id:
                await supabase.table("performance_artists").delete().eq("performance_id", performance.id).execute()
                await supabase.table("performance_works").delete().eq("performance_id", performance.id).execute()
                await supabase.table("performances").delete().eq("performance_id", performance.id).execute()
            raise APIError(str(e)) from None
        except Exception as e:
            raise e
