from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.models.artists import Artist
from music_catalogue.models.exceptions import ValidationError
from music_catalogue.models.persons import Person
from music_catalogue.models.utils import (
    _parse,
    _parse_list,
    validate_date,
    validate_start_and_end_years,
    validate_uuid,
    validate_year,
)


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

    @classmethod
    def from_dict(cls, data: Dict) -> "Genre":
        return cls(
            id=data["genre_id"],
            name=data["name"],
            description=data.get("description"),
        )


class WorkExternalLink(BaseModel):
    label: str
    url: str
    source_verified: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "WorkExternalLink":
        return cls(label=data["label"], url=data["url"], source_verified=data["source_verified"])


class Work(BaseModel):
    id: str
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
    versions: List["Version"] = Field(default_factory=list)
    genres: List[Genre] = Field(default_factory=list)
    credits: List["Credit"] = Field(default_factory=list)
    external_links: List[WorkExternalLink] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Work":
        return cls(
            id=data["work_id"],
            title=data["title"],
            language=data.get("language"),
            titles=data.get("titles"),
            description=data.get("description"),
            identifiers=data.get("identifiers"),
            origin_year_start=data.get("origin_year_start"),
            origin_year_end=data.get("origin_year_end"),
            origin_country=data.get("origin_country"),
            themes=data.get("themes"),
            sentiment=data.get("sentiment"),
            notes=data.get("notes"),
            versions=_parse_list(Version, data.get("versions")),
            genres=_parse_list(Genre, [item.get("genres", None) for item in data.get("work_genres", [])]),
            credits=_parse_list(Credit, data.get("credits")),
        )


class Version(BaseModel):
    id: str
    title: str
    work: Optional[Work] = None
    version_type: VersionType = VersionType.ORIGINAL
    based_on_version: Optional["Version"] = None
    primary_artist: Artist
    release_date: Optional[date] = None
    release_year: Optional[int] = None
    duration_seconds: Optional[int] = None
    bpm: Optional[int] = None
    key_signature: Optional[str] = None
    lyrics_reference: Optional[str] = None
    completeness_level: CompletenessLevel = CompletenessLevel.COMPLETE
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Version":
        return cls(
            id=data["version_id"],
            work=_parse(Work, data.get("work")),
            title=data["title"],
            version_type=VersionType(data["version_type"]),
            based_on_version=_parse(Version, data.get("based_on_version")),
            primary_artist=_parse(Artist, data.get("primary_artist")),
            release_date=datetime.strptime(data.get("release_date"), "%Y-%m-%d").date()
            if data.get("release_date")
            else None,
            release_year=data.get("release_year"),
            duration_seconds=data.get("duration_seconds"),
            bpm=data.get("bpm"),
            key_signature=data.get("key_signature"),
            lyrics_reference=data.get("lyrics_reference"),
            completeness_level=CompletenessLevel(data.get("completeness_level")),
            notes=data.get("notes"),
        )


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


class ReleaseMediaItem(BaseModel):
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


class ReleaseTrack(BaseModel):
    id: str
    version: Version
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
            version=_parse(Version, data.get("version")),
            track_number=data["track_number"],
            disc_number=data.get("disc_number"),
            side=data.get("side"),
            is_hidden=data.get("is_hidden"),
            notes=data.get("notes"),
        )


class Credit(BaseModel):
    id: str
    work: Optional[Work] = None
    version: Optional[Version] = None
    artist: Optional[Artist] = None
    person: Optional[Person] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Credit":
        return cls(
            id=data["credit_id"],
            work=_parse(Work, data.get("work")),
            version=_parse(Version, data.get("version")),
            artist=_parse(Artist, data.get("artist")),
            person=_parse(Person, data.get("person")),
            role=data.get("role"),
            is_primary=data.get("is_primary"),
            credit_order=data.get("credit_order"),
            instruments=data.get("instruments"),
            notes=data.get("notes"),
        )


class WorkCreditCreate(BaseModel):
    artist_id: Optional[str] = None
    person_id: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    def validate(self):
        # Check exactly one of person_id or artist_id
        if (not self.artist_id and not self.person_id) or (self.artist_id and self.person_id):
            raise ValidationError("Either person or artist ID is required for credits")


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

    def validate(self):
        # Check UUIDs are valid
        validate_uuid(self.primary_artist_id)

        # Check date and year validity
        if self.release_date:
            validate_date(self.release_date)
        if self.release_year:
            validate_year(self.release_year)


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
    external_links: Optional[List[WorkExternalLink]] = None

    def validate(self):
        # Check origin year start and end
        validate_start_and_end_years(self.origin_year_start, self.origin_year_end)
        # If credits, validate them
        if self.credits:
            [credit.validate() for credit in self.credits]
        # If versions, validate them
        if self.versions:
            [version.validate() for version in self.versions]
        # If genre IDs, validate they are UUIDs
        if self.genre_ids:
            [validate_uuid(genre_id) for genre_id in self.genre_ids]


Work.model_rebuild()
Version.model_rebuild()
Release.model_rebuild()
ReleaseMediaItem.model_rebuild()
ReleaseTrack.model_rebuild()
