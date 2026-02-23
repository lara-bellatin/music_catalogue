from datetime import date
from typing import List, Optional

from pydantic import BaseModel, model_validator

from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.validation import validate_date, validate_uuid


class ReleaseMediaItemCreate(BaseModel):
    medium_type: str
    format_name: str
    platform_or_vendor: Optional[str] = None
    bitrate_kbps: Optional[int] = None
    sample_rate_hz: Optional[int] = None
    bit_depth: Optional[int] = None
    rpm: Optional[float] = None
    channels: Optional[str] = None
    packaging: Optional[str] = None
    accessories: Optional[str] = None
    pressing_details: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    catalog_variation: Optional[str] = None
    availability_status: Optional[str] = None
    notes: Optional[str] = None


class ReleaseTrackCreate(BaseModel):
    version_id: str
    track_number: int
    disc_number: Optional[int] = None
    side: Optional[str] = None
    is_hidden: Optional[bool] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        validate_uuid(self.version_id)


class ReleaseCreate(BaseModel):
    title: str
    release_date: Optional[date] = None
    release_category: Optional[str] = None
    catalog_number: Optional[str] = None
    publisher_number: Optional[str] = None
    label: Optional[str] = None
    region: Optional[str] = None
    release_stage: Optional[str] = None
    cover_art_url: Optional[str] = None
    total_discs: Optional[int] = None
    total_tracks: Optional[int] = None
    notes: Optional[str] = None
    media_items: Optional[List[ReleaseMediaItemCreate]] = None
    tracks: Optional[List[ReleaseTrackCreate]] = None
    external_links: Optional[List[ExternalLinkCreate]] = None

    @model_validator(mode="after")
    def validate(self):
        if self.release_date:
            validate_date(str(self.release_date))
