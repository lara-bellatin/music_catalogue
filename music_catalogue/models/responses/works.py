from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.work_create import WorkCreate
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import CreditRef, VersionRef
from music_catalogue.models.types import EntityType
from music_catalogue.models.utils import _parse_list
from supabase import PostgrestAPIError


class Genre(BaseModel):
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


class Work(CatalogueModel):
    table_name: ClassVar[str] = "works"
    pk_column: ClassVar[str] = "work_id"
    entity_type: ClassVar[EntityType] = EntityType.WORK
    query: ClassVar[str] = f"""
        work_id,
        title,
        language,
        titles,
        description,
        identifiers,
        origin_year_start,
        origin_year_end,
        origin_country,
        themes,
        sentiment,
        notes,
        versions({VersionRef.query}),
        work_genres(genres(genre_id, name)),
        credits({CreditRef.work_version_query})
    """

    id: str
    title: str
    language: Optional[str] = None
    titles: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    identifiers: Optional[List[Dict[str, Any]]] = None
    origin_year_start: Optional[int] = None
    origin_year_end: Optional[int] = None
    origin_country: Optional[str] = None
    themes: Optional[List[str]] = None
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    versions: List[VersionRef] = Field(default_factory=list)
    genres: List[Genre] = Field(default_factory=list)
    credits: List[CreditRef] = Field(default_factory=list)
    external_links: List[ExternalLink] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Work":
        return cls(
            id=data["work_id"],
            title=data["title"],
            language=data.get("language"),
            titles=data.get("titles"),
            description=data.get("description"),
            identifiers=data.get("identifiers"),
            origin_year_start=data.get("origin_year_start"),
            origin_year_end=data.get("origin_year_end"),
            origin_country=data.get("origin_country"),
            themes=data.get("themes"),
            sentiment=data.get("sentiment"),
            notes=data.get("notes"),
            versions=_parse_list(VersionRef, data.get("versions")),
            genres=_parse_list(Genre, [item.get("genres", None) for item in data.get("work_genres", [])]),
            credits=_parse_list(CreditRef, data.get("credits")),
        )

    @classmethod
    async def create(cls, data: "WorkCreate", exclude: set = None) -> "Work":
        exclude = (exclude or set()) | {"genre_ids", "versions", "credits", "external_links"}
        work = None
        supabase = await get_supabase()

        try:
            work = await super().create(data, exclude=exclude)

            # Create versions
            if data.versions:
                await (
                    supabase.table("versions")
                    .insert(
                        [{"work_id": work.id, **version.model_dump(exclude_none=True)} for version in data.versions]
                    )
                    .execute()
                )

            # Create credits
            if data.credits:
                await (
                    supabase.table("credits")
                    .insert([{"work_id": work.id, **credit.model_dump(exclude_none=True)} for credit in data.credits])
                    .execute()
                )

            # Assign genres
            if data.genre_ids:
                await (
                    supabase.table("work_genres")
                    .insert([{"work_id": work.id, "genre_id": genre_id} for genre_id in data.genre_ids])
                    .execute()
                )

            # Create external links
            if data.external_links:
                await (
                    supabase.table("external_links")
                    .insert(
                        [
                            {
                                "entity_type": EntityType.WORK.value,
                                "entity_id": work.id,
                                **link.model_dump(exclude_none=True),
                                # TODO: Remove hardcoded value once user implementation is done
                                "added_by": "760c6a23-cf19-4e59-89aa-f6921943bc26",
                            }
                            for link in data.external_links
                        ]
                    )
                    .execute()
                )

            # Get work by ID to include complete information
            return await cls.get_by_id(work.id)

        except PostgrestAPIError as e:
            # Roll back work creation and its relationships if any relationship creation fails
            if work and work.id:
                await supabase.table("versions").delete().eq("work_id", work.id).execute()
                await supabase.table("credits").delete().eq("work_id", work.id).execute()
                await supabase.table("work_genres").delete().eq("work_id", work.id).execute()
                await (
                    supabase.table("external_links")
                    .delete()
                    .eq("entity_type", EntityType.WORK)
                    .eq("entity_id", work.id)
                    .execute()
                )
                await supabase.table("works").delete().eq("work_id", work.id).execute()
            raise APIError(str(e)) from None
        except Exception as e:
            raise e
