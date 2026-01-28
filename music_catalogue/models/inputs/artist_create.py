from typing import List, Optional

from pydantic import BaseModel, model_validator

from music_catalogue.models.types import ArtistType
from music_catalogue.models.validation import validate_start_and_end_years, validate_uuid


class ArtistMembershipCreate(BaseModel):
    person_id: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        try:
            # Validate person ID format
            validate_uuid(self.person_id)
            # Validate start or end years
            validate_start_and_end_years(self.start_year, self.end_year)
        except ValueError as e:
            raise ValueError(f"Invalid member configuration for person with ID {self.person_id}: {str(e)}") from None


class ArtistCreate(BaseModel):
    artist_type: ArtistType
    display_name: str
    sort_name: Optional[str] = None
    alternative_names: Optional[List[str]] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    person_id: Optional[str] = None
    members: Optional[List[ArtistMembershipCreate]] = None

    @model_validator(mode="after")
    def validate(self):
        # Raise for invalid start or end years
        validate_start_and_end_years(self.start_year, self.end_year)

        if self.artist_type == ArtistType.SOLO:
            # Raise if no person_id for SOLO artist
            if not self.person_id:
                raise ValueError("Missing person ID for SOLO type artist")
            # Validate person UUID and raise if invalid
            validate_uuid(self.person_id)
            # Raise if there are members for SOLO artist
            if self.members:
                raise ValueError("There cannot be members for a SOLO type artist")
        else:
            # Raise if no members for GROUP artist
            if not self.members:
                raise ValueError("Missing members for GROUP type artist")
            # Raise if there's a person_id for artist
            if self.person_id:
                raise ValueError("Invalid assignment of person to GROUP type artist")
