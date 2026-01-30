from typing import Dict, List, Optional

from pydantic import BaseModel

from music_catalogue.models.responses.references import PersonRef
from music_catalogue.models.types import ArtistType
from music_catalogue.models.utils import _parse, _parse_list


class Artist(BaseModel):
    id: str
    person: Optional[PersonRef] = None
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
            person=_parse(PersonRef, data.get("person")),
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
    person: Optional[PersonRef] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtistMembership":
        return cls(
            id=data["membership_id"],
            person=_parse(PersonRef, data.get("person")),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            role=data.get("role"),
            notes=data.get("notes"),
        )
