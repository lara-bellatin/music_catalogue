from typing import Dict, List, Optional

from pydantic import BaseModel

from music_catalogue.models.responses.persons import Person
from music_catalogue.models.types import ArtistType
from music_catalogue.models.utils import _parse, _parse_list


class Artist(BaseModel):
    id: str
    person: Optional[Person] = None
    artist_type: ArtistType
    display_name: str
    sort_name: Optional[str] = None
    alternative_names: Optional[List[str]] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    members: Optional[List["ArtistMembership"]] = None

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
            members=_parse_list(ArtistMembership, data.get("artist_memberships", None)) or None,
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
            notes=data.get("notes"),
        )


Artist.model_rebuild()
ArtistMembership.model_rebuild()
