from datetime import date, datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.version_create import VersionCreate
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import ArtistRef, CreditRef, VersionRef, WorkRef
from music_catalogue.models.types import CompletenessLevel, EntityType, VersionType
from music_catalogue.models.utils import (
    _parse,
    _parse_list,
)
from supabase import PostgrestAPIError


class Version(CatalogueModel):
    table_name: ClassVar[str] = "versions"
    pk_column: ClassVar[str] = "version_id"
    entity_type: ClassVar[EntityType] = EntityType.VERSION
    ref_model: ClassVar[BaseModel] = VersionRef
    query: ClassVar[str] = f"""
        version_id,
        title,
        work:works({WorkRef.query}),
        version_type,
        based_on_version:based_on_version_id({VersionRef.query}),
        derived_versions:versions({VersionRef.query}),
        primary_artist:artists({ArtistRef.query}),
        release_date,
        release_year,
        duration_seconds,
        bpm,
        key_signature,
        lyrics_reference,
        completeness_level,
        identifiers,
        notes,
        credits({CreditRef.work_version_query})
    """

    id: str
    title: str
    work: Optional[WorkRef] = None
    version_type: VersionType = VersionType.ORIGINAL
    based_on_version: Optional[VersionRef] = None
    primary_artist: ArtistRef
    release_date: Optional[date] = None
    release_year: Optional[int] = None
    duration_seconds: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    lyrics_reference: Optional[str] = None
    completeness_level: CompletenessLevel = CompletenessLevel.COMPLETE
    identifiers: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    derived_versions: List[VersionRef] = Field(default_factory=list)
    credits: List[CreditRef] = Field(default_factory=list)
    external_links: List[ExternalLink] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Version":
        return cls(
            id=data["version_id"],
            work=_parse(WorkRef, data.get("work")),
            title=data["title"],
            version_type=VersionType(data["version_type"]),
            based_on_version=_parse(VersionRef, data["based_on_version"]),
            primary_artist=_parse(ArtistRef, data.get("primary_artist")),
            release_date=datetime.strptime(data.get("release_date"), "%Y-%m-%d").date()
            if data.get("release_date")
            else None,
            release_year=data.get("release_year"),
            duration_seconds=data.get("duration_seconds"),
            bpm=data.get("bpm"),
            key_signature=data.get("key_signature"),
            lyrics_reference=data.get("lyrics_reference"),
            completeness_level=CompletenessLevel(data.get("completeness_level")),
            identifiers=data.get("identifiers"),
            notes=data.get("notes"),
            credits=_parse_list(CreditRef, data.get("credits")),
            derived_versions=_parse_list(VersionRef, data.get("derived_versions")),
        )

    @classmethod
    async def create(cls, data: "VersionCreate", exclude: set = None) -> "Version":
        exclude = (exclude or set()) | {"credits", "external_links"}
        work = None
        supabase = await get_supabase()

        try:
            version = await super().create(data, exclude=exclude)

            # Create credits
            if data.credits:
                await (
                    supabase.table("credits")
                    .insert(
                        [{"version_id": version.id, **credit.model_dump(exclude_none=True)} for credit in data.credits]
                    )
                    .execute()
                )

            # Get version by ID to include complete information
            return await cls.get_by_id(version.id)

        except PostgrestAPIError as e:
            # Roll back work creation and its relationships if any relationship creation fails
            if work and work.id:
                await supabase.table("credits").delete().eq("work_id", work.id).execute()
                await supabase.table("works").delete().eq("work_id", work.id).execute()
            raise APIError(str(e)) from None
        except Exception as e:
            raise e
