from datetime import date
from typing import List, Optional

from pydantic import BaseModel, model_validator

from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.validation import validate_date, validate_uuid


class PerformanceArtistCreate(BaseModel):
    artist_id: Optional[str] = None
    person_id: Optional[str] = None
    role: Optional[str] = None
    billing_order: Optional[int] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        if (not self.artist_id and not self.person_id) or (self.artist_id and self.person_id):
            raise ValueError("Exactly one of artist_id or person_id is required")
        if self.artist_id:
            validate_uuid(self.artist_id)
        if self.person_id:
            validate_uuid(self.person_id)


class PerformanceWorkCreate(BaseModel):
    work_id: Optional[str] = None
    version_id: Optional[str] = None
    set_order: Optional[int] = None
    set_name: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        if not self.work_id and not self.version_id:
            raise ValueError("At least one of work_id or version_id is required")
        if self.work_id:
            validate_uuid(self.work_id)
        if self.version_id:
            validate_uuid(self.version_id)


class PerformanceCreate(BaseModel):
    name: str
    performance_date: Optional[date] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    artists: Optional[List[PerformanceArtistCreate]] = None
    works: Optional[List[PerformanceWorkCreate]] = None
    external_links: Optional[List[ExternalLinkCreate]] = None

    @model_validator(mode="after")
    def validate(self):
        validate_date(self.performance_date)
