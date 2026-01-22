from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from music_catalogue.models.exceptions import ValidationError
from music_catalogue.models.persons import Person
from music_catalogue.models.utils import _parse, _parse_list, validate_start_and_end_years, validate_uuid


class ArtistType(str, Enum):
    SOLO = "solo"
    GROUP = "group"


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


class ArtistMembershipCreate(BaseModel):
    person_id: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    def validate(self):
        try:
            # Validate person ID format
            validate_uuid(self.person_id)
            # Validate start or end years
            validate_start_and_end_years(self.start_year, self.end_year)
        except ValidationError as e:
            raise ValidationError(
                f"Invalid member configuration for person with ID {self.person_id}: {str(e)}"
            ) from None


class ArtistCreate(BaseModel):
    artist_type: ArtistType
    display_name: str
    sort_name: Optional[str] = None
    alternative_names: Optional[List[str]] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    person_id: Optional[str] = None
    members: Optional[List[ArtistMembershipCreate]] = None

    def validate(self):
        # Raise for invalid start or end years
        validate_start_and_end_years(self.start_year, self.end_year)

        if self.artist_type == ArtistType.SOLO:
            # Raise if no person_id for SOLO artist
            if not self.person_id:
                raise ValidationError("Missing person ID for SOLO type artist")
            # Validate person UUID and raise if invalid
            validate_uuid(self.person_id)
            # Raise if there are members for SOLO artist
            if self.members:
                raise ValidationError("There cannot be members for a SOLO type artist")
        else:
            # Raise if no members for GROUP artist
            if not self.members:
                raise ValidationError("Missing members for GROUP type artist")
            # Raise if there's a person_id for artist
            if self.person_id:
                raise ValidationError("Invalid assignment of person to GROUP type artist")
            # Validate person ID and start and end years for each member
            for member in self.members:
                member.validate()


Artist.model_rebuild()
ArtistMembership.model_rebuild()
