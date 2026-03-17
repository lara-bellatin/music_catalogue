from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.version_create import VersionCreate
from music_catalogue.models.inputs.work_create import WorkCreate
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.genres import Genre
from music_catalogue.models.responses.references import CreditRef, PerformanceRef, VersionRef, WorkRef
from music_catalogue.models.responses.versions import Version
from music_catalogue.models.types import EntityType
from music_catalogue.models.utils import _parse, _parse_list
from supabase import PostgrestAPIError


class Work(CatalogueModel):
    table_name: ClassVar[str] = "works"
    pk_column: ClassVar[str] = "work_id"
    entity_type: ClassVar[EntityType] = EntityType.WORK
    ref_model: ClassVar[BaseModel] = WorkRef
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
        based_on_work:based_on_work_id({WorkRef.query}),
        derived_works:works({WorkRef.query}),
        versions({VersionRef.query}),
        work_genres(genres(genre_id, name)),
        credits({CreditRef.work_version_query}),
        performance_works(performances({PerformanceRef.query}))
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
    based_on_work: Optional[WorkRef] = None
    derived_works: List[WorkRef] = Field(default_factory=list)
    versions: List[VersionRef] = Field(default_factory=list)
    genres: List[Genre] = Field(default_factory=list)
    credits: List[CreditRef] = Field(default_factory=list)
    performances: List[PerformanceRef] = Field(default_factory=list)
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
            based_on_work=_parse(WorkRef, data.get("based_on_work")),
            derived_works=_parse_list(WorkRef, data.get("derived_works")),
            versions=_parse_list(VersionRef, data.get("versions")),
            genres=_parse_list(Genre, [item.get("genres", None) for item in data.get("work_genres", [])]),
            performances=_parse_list(
                PerformanceRef, [item.get("performances") for item in data.get("performance_works", [])]
            ),
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
                # TODO: Implement bulk create
                for version in data.versions:
                    await Version.create(VersionCreate(work_id=work.id, **version.model_dump(exclude_none=True)))

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

            # Get work by ID to include complete information
            return await cls.get_by_id(work.id)

        except PostgrestAPIError as e:
            # Roll back work creation and its relationships if any relationship creation fails
            if work and work.id:
                await supabase.table("versions").delete().eq("work_id", work.id).execute()
                await supabase.table("credits").delete().eq("work_id", work.id).execute()
                await supabase.table("work_genres").delete().eq("work_id", work.id).execute()
            raise APIError(str(e)) from None
        except Exception as e:
            raise e
