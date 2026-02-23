from datetime import date, datetime
from typing import ClassVar, Dict, List, Optional

from pydantic import BaseModel

from music_catalogue.models.types import ArtistType, MediumType, ReleaseCategory, VersionType
from music_catalogue.models.utils import _parse


class ArtistRef(BaseModel):
    query: ClassVar[str] = "artist_id, display_name, artist_type"

    id: str
    name: str
    artist_type: ArtistType

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtistRef":
        return cls(
            id=data["artist_id"],
            name=data["display_name"],
            artist_type=ArtistType(data["artist_type"]),
        )


class PersonRef(BaseModel):
    query: ClassVar[str] = "person_id, legal_name"

    id: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonRef":
        return cls(
            id=data["person_id"],
            name=data["legal_name"],
        )


class WorkRef(BaseModel):
    query: ClassVar[str] = "work_id, title,language"

    id: str
    title: str
    language: str

    @classmethod
    def from_dict(cls, data: Dict) -> "WorkRef":
        return cls(
            id=data["work_id"],
            title=data["title"],
            language=data["language"],
        )


class VersionRef(BaseModel):
    query: ClassVar[str] = f"""
        version_id,
        title,
        version_type,
        primary_artist:artists!fk_versions_primary_artist({ArtistRef.query}),
        release_year,
        completeness_level
    """

    id: str
    title: str
    work: Optional[WorkRef] = None
    version_type: VersionType
    primary_artist: Optional[ArtistRef] = None
    release_year: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "VersionRef":
        return cls(
            id=data["version_id"],
            title=data["title"],
            work=_parse(WorkRef, data.get("work", None)) or None,
            version_type=VersionType(data["version_type"]),
            primary_artist=_parse(ArtistRef, data.get("primary_artist", None)) or None,
            release_year=data.get("release_year"),
        )


class ReleaseRef(BaseModel):
    query: ClassVar[str] = "release_id, title, release_date, release_category"

    id: str
    title: str
    release_year: Optional[int] = None
    release_category: ReleaseCategory = ReleaseCategory.SINGLE

    @classmethod
    def from_dict(cls, data: Dict) -> "ReleaseRef":
        return cls(
            id=data["release_id"],
            title=data["title"],
            release_date=datetime.strptime(data.get("release_date"), "%Y-%m-%d").year
            if data.get("release_date")
            else None,
            release_category=ReleaseCategory(data.get("release_category")),
        )


class ReleaseMediaItemRef(BaseModel):
    id: str
    medium_type: MediumType
    format_name: str
    release: Optional[ReleaseRef] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ReleaseMediaItemRef":
        return cls(
            id=data["media_item_id"],
            release=_parse(ReleaseRef, data.get("release")),
            medium_type=MediumType(data["medium_type"]),
            format_name=data["format_name"],
        )


class CreditRef(BaseModel):
    work_version_query: ClassVar[str] = f"""
        credit_id,
        role,
        is_primary,
        credit_order,
        notes,
        artist:artists({ArtistRef.query}),
        person:persons({PersonRef.query})
    """
    artist_person_query: ClassVar[str] = f"""
        credit_id,
        role,
        is_primary,
        credit_order,
        notes,
        work:works({WorkRef.query}),
        version:versions({VersionRef.query})
    """

    role: str
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None
    artist: Optional[ArtistRef] = None
    person: Optional[PersonRef] = None
    work: Optional[WorkRef] = None
    version: Optional[VersionRef] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "CreditRef":
        return cls(
            role=data["role"],
            is_primary=data["is_primary"],
            credit_order=data.get("credit_order"),
            instruments=data.get("instruments"),
            notes=data.get("notes"),
            artist=_parse(ArtistRef, data.get("artist")),
            person=_parse(PersonRef, data.get("person")),
            work=_parse(WorkRef, data.get("work")),
            version=_parse(VersionRef, data.get("version")),
        )


class PerformanceArtistRef(BaseModel):
    query: ClassVar[str] = f"""
        performance_artist_id,
        role,
        billing_order,
        notes,
        artist:artists({ArtistRef.query}),
        person:persons({PersonRef.query})
    """

    role: Optional[str] = None
    billing_order: Optional[int] = None
    notes: Optional[str] = None
    artist: Optional[ArtistRef] = None
    person: Optional[PersonRef] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "PerformanceArtistRef":
        return cls(
            role=data.get("role"),
            billing_order=data.get("billing_order"),
            notes=data.get("notes"),
            artist=_parse(ArtistRef, data.get("artist")),
            person=_parse(PersonRef, data.get("person")),
        )


class PerformanceWorkRef(BaseModel):
    query: ClassVar[str] = f"""
        performance_work_id,
        set_order,
        set_name,
        notes,
        work:works({WorkRef.query}),
        version:versions({VersionRef.query})
    """

    set_order: Optional[int] = None
    set_name: Optional[str] = None
    notes: Optional[str] = None
    work: Optional[WorkRef] = None
    version: Optional[VersionRef] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "PerformanceWorkRef":
        return cls(
            set_order=data.get("set_order"),
            set_name=data.get("set_name"),
            notes=data.get("notes"),
            work=_parse(WorkRef, data.get("work")),
            version=_parse(VersionRef, data.get("version")),
        )


class PerformanceRef(BaseModel):
    query: ClassVar[str] = "performance_id, name, performance_date, venue, city"

    id: str
    name: str
    performance_date: Optional[date] = None
    venue: Optional[str] = None
    city: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "PerformanceRef":
        return cls(
            id=data["performance_id"],
            name=data["name"],
            performance_date=datetime.strptime(data["performance_date"], "%Y-%m-%d").date()
            if data.get("performance_date")
            else None,
            venue=data.get("venue"),
            city=data.get("city"),
        )
