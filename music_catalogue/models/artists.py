from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date
from enum import Enum

from music_catalogue.models.utils import _parse, _parse_list

class ArtistType(str, Enum):
    SOLO = "solo"
    GROUP = "group"


class Person(BaseModel):
    id: str
    legal_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    pronouns: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Person":
        return cls(
            id=data["person_id"],
            legal_name=data["legal_name"],
            birth_date=date.fromisoformat(data.get("birth_date")) if data.get("birth_date") else None,
            death_date=date.fromisoformat(data.get("death_date")) if data.get("death_date") else None,
            pronouns=data.get("pronouns"),
            notes=data.get("notes"),
        )


class Artist(BaseModel):
    id: str
    person: Optional[Person] = None
    artist_type: ArtistType
    display_name: str
    sort_name: Optional[str] = None
    alternative_names: List[str] = Field(default_factory=list)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    members: List["ArtistMembership"] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Artist":
        return cls(
            id=data["artist_id"],
            person=_parse(Person, data.get("person")),
            artist_type=ArtistType(data["artist_type"]),
            display_name=data["display_name"],
            sort_name=data.get("sort_name"),
            alternative_names=data.get("alternative_names"),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            members=_parse_list(ArtistMembership, data.get("artist_memberships")),
        )


class ArtistMembership(BaseModel):
    id: str
    artist: Optional[Artist] = None
    person: Optional[Person] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtistMembership":
        return cls(
            id=data["membership_id"],
            artist=_parse(Artist, data.get("artist")),
            person=_parse(Person, data.get("person")),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            role=data.get("role"),
            notes=data.get("notes")
        )


Artist.model_rebuild()
ArtistMembership.model_rebuild()