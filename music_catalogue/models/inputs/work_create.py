from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, model_validator

from music_catalogue.models.types import CompletenessLevel, VersionType
from music_catalogue.models.validation import (
    validate_date,
    validate_start_and_end_years,
    validate_uuid,
    validate_year,
)


# CREATE
class WorkCreditCreate(BaseModel):
    artist_id: Optional[str] = None
    person_id: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        # Check exactly one of person_id or artist_id
        if (not self.artist_id and not self.person_id) or (self.artist_id and self.person_id):
            raise ValueError("Either person or artist ID is required for credits")


class WorkVersionCreate(BaseModel):
    title: str
    version_type: VersionType = VersionType.ORIGINAL
    primary_artist_id: str
    release_date: Optional[date] = None
    release_year: Optional[int] = None
    duration_seconds: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    lyrics_reference: Optional[str] = None
    completeness_level: CompletenessLevel = CompletenessLevel.COMPLETE
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        # Check UUIDs are valid
        validate_uuid(self.primary_artist_id)

        # Check date and year validity
        if self.release_date:
            validate_date(self.release_date)
        if self.release_year:
            validate_year(self.release_year)


class WorkExternalLinkCreate(BaseModel):
    label: str
    url: str
    source_verified: bool = False


class WorkCreate(BaseModel):
    title: str
    language: Optional[str] = None
    titles: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    identifiers: Optional[List[Dict[str, Any]]] = None
    origin_year_start: Optional[int] = None
    origin_year_end: Optional[int] = None
    origin_country: Optional[str] = None
    themes: Optional[List[str]] = None
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    genre_ids: Optional[List[str]] = None
    versions: Optional[List[WorkVersionCreate]] = None
    credits: Optional[List[WorkCreditCreate]] = None
    external_links: Optional[List[WorkExternalLinkCreate]] = None

    @model_validator(mode="after")
    def validate(self):
        # Check origin year start and end
        validate_start_and_end_years(self.origin_year_start, self.origin_year_end)
        # If genre IDs, validate they are UUIDs
        if self.genre_ids:
            [validate_uuid(genre_id) for genre_id in self.genre_ids]
