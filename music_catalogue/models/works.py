from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import date
from enum import Enum

from music_catalogue.models.artists import Artist, Person


class VersionType(str, Enum):
    ORIGINAL = "original"
    COVER = "cover"
    REMIX = "remix"
    LIVE = "live"
    MASHUP = "mashup"
    DEMO = "demo"
    RADIO_EDIT = "radio_edit"
    OTHER = "other"


class CompletenessLevel(str, Enum):
    SPARSE = "sparse"
    PARTIAL = "partial"
    COMPLETE = "complete"


class ReleaseCategory(str, Enum):
    SINGLE = "single"
    EP = "ep"
    ALBUM = "album"
    COMPILATION = "compilation"
    LIVE = "live"
    SOUNDTRACK = "soundtrack"
    DELUXE = "deluxe"
    OTHER = "other"


class ReleaseStage(str, Enum):
    INITIAL = "initial"
    REISSUE = "reissue"
    REMASTER = "remaster"
    ANNIVERSARY = "anniversary"
    OTHER = "other"


class MediumType(str, Enum):
    DIGITAL = "digital"
    PHYSICAL = "physical"


class AudioChannel(str, Enum):
    MONO = "mono"
    STEREO = "stereo"
    SURROUND = "surround"
    DOLBY_ATMOS = "dolby_atmos"


class AvailabilityStatus(str, Enum):
    IN_PRINT = "in_print"
    LIMITED = "limited"
    OUT_OF_PRINT = "out_of_print"
    DIGITAL_ONLY = "digital_only"


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class Work(BaseModel):
    id: str
    title: str
    language: str
    titles: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    origin_year_start: Optional[int] = None
    origin_year_end: Optional[int] = None
    origin_country: Optional[int] = None
    themes: Optional[List[str]] = None
    sentiment: Optional[str] = None
    notes: Optional[str] = None
    versions: List["Version"] = Field(default_factory=list)
    genres: List[Genre] = Field(default_factory=list)

class Version(BaseModel):
    id: str
    work: Work
    title: str
    version_type: VersionType = VersionType.ORIGINAL
    based_on_version: Optional["Version"] = None
    primary_artist: Artist
    release_date: Optional[date] = None
    duration_seconds: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    lyrics_reference: Optional[str] = None
    completeness_level: CompletenessLevel = CompletenessLevel.COMPLETE
    notes: Optional[str] = None


class Release(BaseModel):
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
    media_items: Optional[List["ReleaseMediaItem"]] = None


class ReleaseMediaItem(BaseModel):
    id: str
    release: Release
    medium_type: MediumType
    format_name: str
    platform_or_vendor: Optional[str] = None
    bitrate_kbps: Optional[int] = None
    sample_rate_hz: Optional[int] = None
    bit_depth: Optional[int] = None
    rpm: Optional[float] = None
    channels: Optional[AudioChannel] = None
    packaging: Optional[str] = None
    accesories: Optional[str] = None
    pressing_details: Optional[Any] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    catalog_variation: Optional[str] = None
    availability_status: AvailabilityStatus = AvailabilityStatus.IN_PRINT
    notes: Optional[str] = None


class ReleaseTrack(BaseModel):
    id: str
    release: Release
    version: Version
    disc_number: int = 1
    track_number: int
    side: Optional[str]
    is_hidden: bool = False
    notes: Optional[str] = None

class Credit(BaseModel):
    id: str
    version: Version
    artist: Optional[Artist] = None
    person: Optional[Person] = None
    role: str
    is_primary: bool = False
    credit_order: int
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None


Work.model_rebuild()
Version.model_rebuild()
Release.model_rebuild()
ReleaseMediaItem.model_rebuild()
ReleaseTrack.model_rebuild()