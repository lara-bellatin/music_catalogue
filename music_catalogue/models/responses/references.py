from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from music_catalogue.models.types import ArtistType, MediumType, ReleaseCategory, VersionType
from music_catalogue.models.utils import _parse


class ArtistRef(BaseModel):
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
    id: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonRef":
        return cls(
            id=data["person_id"],
            name=data["legal_name"],
        )


class WorkRef(BaseModel):
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
            primary_artist=_parse(ArtistRef, data.get("artist", None)) or None,
            release_year=data.get("release_year"),
        )


class ReleaseRef(BaseModel):
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
    role: str
    is_primary: bool
    work: Optional[WorkRef] = None
    version: Optional[VersionRef] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "CreditRef":
        return cls(
            role=data["role"],
            is_primary=data["is_primary"],
            work=_parse(WorkRef, data.get("work")),
            version=_parse(WorkRef, data.get("version")),
        )
