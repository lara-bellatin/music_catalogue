from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import ArtistRef, VersionRef, WorkRef
from music_catalogue.models.utils import _parse, _parse_list


class PersonCredit(BaseModel):
    id: str
    work: Optional[WorkRef] = None
    version: Optional[VersionRef] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonCredit":
        return cls(
            id=data["credit_id"],
            work=_parse(WorkRef, data.get("work")),
            version=_parse(VersionRef, data.get("version")),
            role=data.get("role"),
            is_primary=data.get("is_primary"),
            credit_order=data.get("credit_order"),
            instruments=data.get("instruments"),
            notes=data.get("notes"),
        )


class PersonArtistMembership(BaseModel):
    id: str
    artist: Optional[ArtistRef] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonArtistMembership":
        return cls(
            id=data["membership_id"],
            artist=_parse(ArtistRef, data.get("artist")),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            role=data.get("role"),
            notes=data.get("notes"),
        )


class Person(BaseModel):
    id: str
    legal_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    pronouns: Optional[str] = None
    notes: Optional[str] = None
    credits: List[PersonCredit] = Field(default_factory=list)
    memberships: Optional[List[PersonArtistMembership]] = None
    external_links: Optional[List[ExternalLink]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Person":
        return cls(
            id=data["person_id"],
            legal_name=data["legal_name"],
            birth_date=date.fromisoformat(data.get("birth_date")) if data.get("birth_date") else None,
            death_date=date.fromisoformat(data.get("death_date")) if data.get("death_date") else None,
            pronouns=data.get("pronouns"),
            notes=data.get("notes"),
            credits=_parse_list(PersonCredit, data.get("credits")),
            memberships=_parse_list(PersonArtistMembership, data.get("artist_memberships")) or None,
        )
