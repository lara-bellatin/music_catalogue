from datetime import date
from typing import List, Optional

from pydantic import BaseModel, model_validator

from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.inputs.credit_create import CreditCreate
from music_catalogue.models.types import CompletenessLevel, VersionType
from music_catalogue.models.validation import (
    validate_date,
    validate_uuid,
    validate_year,
)


# CREATE
class VersionCreate(BaseModel):
    title: str
    work_id: str
    primary_artist_id: str
    version_type: VersionType = VersionType.ORIGINAL
    based_on_version_id: Optional[str] = None
    release_date: Optional[date] = None
    release_year: Optional[int] = None
    duration_seconds: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    lyrics_reference: Optional[str] = None
    completeness_level: CompletenessLevel = CompletenessLevel.COMPLETE
    notes: Optional[str] = None
    credits: Optional[List[CreditCreate]] = None
    external_links: Optional[List[ExternalLinkCreate]] = None

    @model_validator(mode="after")
    def validate(self):
        # Check release date
        if self.release_date:
            validate_date(str(self.release_date))

        # Check release year
        if self.release_year:
            validate_year(self.release_year)

        # Validate UUIDS
        validate_uuid(self.work_id)
        validate_uuid(self.primary_artist_id)
        if self.based_on_version_id:
            validate_uuid(self.based_on_version_id)
