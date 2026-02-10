from datetime import date, datetime
from typing import ClassVar, Dict, List, Optional

from pydantic import Field

from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import ArtistRef, CreditRef, VersionRef, WorkRef
from music_catalogue.models.types import CompletenessLevel, EntityType, VersionType
from music_catalogue.models.utils import (
    _parse,
    _parse_list,
)


class Version(CatalogueModel):
    table_name: ClassVar[str] = "versions"
    pk_column: ClassVar[str] = "version_id"
    entity_type: ClassVar[EntityType] = EntityType.VERSION
    query: ClassVar[str] = f"""
        version_id,
        title,
        work:works({WorkRef.query}),
        version_type,
        based_on_version:versions({VersionRef.query}),
        primary_artist:artists({ArtistRef.query}),
        release_date,
        release_year,
        duration_seconds,
        bpm,
        key_signature,
        lyrics_reference,
        completeness_level,
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
    notes: Optional[str] = None
    credits: List[CreditRef] = Field(default_factory=list)
    external_links: List[ExternalLink] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Version":
        return cls(
            id=data["version_id"],
            work=_parse(WorkRef, data.get("work")),
            title=data["title"],
            version_type=VersionType(data["version_type"]),
            based_on_version=_parse(VersionRef, data.get("based_on_version")),
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
            notes=data.get("notes"),
            credits=_parse_list(CreditRef, data.get("credits")),
        )
