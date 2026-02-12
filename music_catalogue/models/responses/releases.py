from datetime import date, datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.responses.references import ReleaseRef, VersionRef
from music_catalogue.models.types import (
    AudioChannel,
    AvailabilityStatus,
    EntityType,
    MediumType,
    ReleaseCategory,
    ReleaseStage,
)
from music_catalogue.models.utils import (
    _parse,
    _parse_list,
)


class Release(CatalogueModel):
    table_name: ClassVar[str] = "works"
    pk_column: ClassVar[str] = "work_id"
    entity_type: ClassVar[EntityType] = EntityType.WORK
    query: ClassVar[str] = ""
    entity_type: ClassVar[EntityType] = EntityType.RELEASE
    ref_model: ClassVar[BaseModel] = ReleaseRef

    id: str
    title: str
    release_date: Optional[date] = None
    release_category: ReleaseCategory = ReleaseCategory.SINGLE
    catalog_number: Optional[str] = None
    publisher_number: Optional[str] = None
    label: Optional[str] = None
    region: Optional[str] = None
    release_stage: ReleaseStage = ReleaseStage.INITIAL
    cover_art_url: Optional[str] = None
    total_discs: int = 1
    total_tracks: int
    notes: Optional[str] = None
    media_items: List["ReleaseMediaItem"] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Release":
        return cls(
            id=data["release_id"],
            title=data["title"],
            release_date=datetime.strptime(data.get("release_date"), "%Y-%m-%d").date()
            if data.get("release_date")
            else None,
            release_category=ReleaseCategory(data.get("release_category")),
            catalog_number=data.get("catalog_number"),
            publisher_number=data.get("publisher_number"),
            label=data.get("label"),
            region=data.get("region"),
            release_stage=ReleaseStage(data.get("release_stage")),
            cover_art_url=data.get("cover_art_url"),
            total_discs=data.get("total_discs"),
            total_tracks=data.get("total_tracks"),
            notes=data.get("notes"),
            media_items=_parse_list(ReleaseMediaItem, data.get("release_media_items")),
        )


class ReleaseMediaItem(CatalogueModel):
    id: str
    medium_type: MediumType
    format_name: str
    release: Optional[Release] = None
    platform_or_vendor: Optional[str] = None
    bitrate_kbps: Optional[int] = None
    sample_rate_hz: Optional[int] = None
    bit_depth: Optional[int] = None
    rpm: Optional[float] = None
    channels: Optional[AudioChannel] = None
    packaging: Optional[str] = None
    accessories: Optional[str] = None
    pressing_details: Optional[Any] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    catalog_variation: Optional[str] = None
    availability_status: AvailabilityStatus = AvailabilityStatus.IN_PRINT
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ReleaseMediaItem":
        return cls(
            id=data["media_item_id"],
            release=_parse(Release, data.get("release")),
            medium_type=MediumType(data["medium_type"]),
            format_name=data["format_name"],
            platform_or_vendor=data.get("platform_or_vendor"),
            bitrate_kbps=data.get("bitrate_kbps"),
            sample_rate_hz=data.get("sample_rate_hz"),
            bit_depth=data.get("bit_depth"),
            rpm=data.get("rpm"),
            channels=AudioChannel(data.get("channels")),
            packaging=data.get("packaging"),
            accessories=data.get("accessories"),
            pressing_details=data.get("pressing_details"),
            sku=data.get("sku"),
            barcode=data.get("barcode"),
            catalog_variation=data.get("catalog_variation"),
            availability_status=AvailabilityStatus(data.get("availability_status")),
        )


class ReleaseTrack(CatalogueModel):
    id: str
    version: VersionRef
    track_number: int
    disc_number: int = 1
    side: Optional[str] = None
    release: Optional[Release] = None
    is_hidden: bool = False
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ReleaseTrack":
        return cls(
            id=data["release_track_id"],
            release=_parse(Release, data.get("release")),
            version=_parse(VersionRef, data.get("version")),
            track_number=data["track_number"],
            disc_number=data.get("disc_number"),
            side=data.get("side"),
            is_hidden=data.get("is_hidden"),
            notes=data.get("notes"),
        )
