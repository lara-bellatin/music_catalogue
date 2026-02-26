from datetime import date, datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import ArtistRef, CreditRef, ReleaseRef, VersionRef
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
from supabase import PostgrestAPIError


class Release(CatalogueModel):
    table_name: ClassVar[str] = "releases"
    pk_column: ClassVar[str] = "release_id"
    entity_type: ClassVar[EntityType] = EntityType.RELEASE
    ref_model: ClassVar[BaseModel] = ReleaseRef
    query: ClassVar[str] = f"""
        release_id,
        release_title,
        release_date,
        release_category,
        catalog_number,
        publisher_number,
        label,
        region,
        release_stage,
        cover_art_url,
        total_discs,
        total_tracks,
        identifiers,
        notes,
        primary_artist:artists!fk_releases_primary_artist({ArtistRef.query}),
        release_media_items(
            media_item_id,
            medium_type,
            format_name,
            platform_or_vendor,
            bitrate_kbps,
            sample_rate_hz,
            bit_depth,
            rpm,
            channels,
            packaging,
            accessories,
            pressing_details,
            sku,
            barcode,
            catalog_variation,
            availability_status,
            notes
        ),
        release_tracks(
            release_track_id,
            track_number,
            disc_number,
            side,
            is_hidden_track,
            identifiers,
            notes,
            version:versions({VersionRef.query})
        ),
        credits({CreditRef.work_version_query})
    """

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
    identifiers: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    primary_artist: Optional[ArtistRef] = None
    media_items: List["ReleaseMediaItem"] = Field(default_factory=list)
    tracks: List["ReleaseTrack"] = Field(default_factory=list)
    credits: List[CreditRef] = Field(default_factory=list)
    external_links: List[ExternalLink] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Release":
        return cls(
            id=data["release_id"],
            title=data["release_title"],
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
            identifiers=data.get("identifiers"),
            notes=data.get("notes"),
            primary_artist=_parse(ArtistRef, data.get("primary_artist")),
            media_items=_parse_list(ReleaseMediaItem, data.get("release_media_items")),
            tracks=_parse_list(ReleaseTrack, data.get("release_tracks")),
            credits=_parse_list(CreditRef, data.get("credits")),
        )

    @classmethod
    async def create(cls, data, exclude: set = None) -> "Release":
        exclude = (exclude or set()) | {"media_items", "tracks", "credits", "external_links"}
        supabase = await get_supabase()
        release = None

        try:
            release = await super().create(data, exclude=exclude)

            if data.media_items:
                await (
                    supabase.table("release_media_items")
                    .insert(
                        [{"release_id": release.id, **item.model_dump(exclude_none=True)} for item in data.media_items]
                    )
                    .execute()
                )

            if data.tracks:
                await (
                    supabase.table("release_tracks")
                    .insert(
                        [{"release_id": release.id, **track.model_dump(exclude_none=True)} for track in data.tracks]
                    )
                    .execute()
                )

            if data.credits:
                await (
                    supabase.table("credits")
                    .insert(
                        [{"release_id": release.id, **credit.model_dump(exclude_none=True)} for credit in data.credits]
                    )
                    .execute()
                )

            return await cls.get_by_id(release.id)

        except PostgrestAPIError as e:
            if release and release.id:
                await supabase.table("release_media_items").delete().eq("release_id", release.id).execute()
                await supabase.table("release_tracks").delete().eq("release_id", release.id).execute()
                await supabase.table("credits").delete().eq("release_id", release.id).execute()
                await supabase.table("releases").delete().eq("release_id", release.id).execute()
            raise APIError(str(e)) from None
        except Exception as e:
            raise e


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
            channels=AudioChannel(data["channels"]) if data.get("channels") else None,
            packaging=data.get("packaging"),
            accessories=data.get("accessories"),
            pressing_details=data.get("pressing_details"),
            sku=data.get("sku"),
            barcode=data.get("barcode"),
            catalog_variation=data.get("catalog_variation"),
            availability_status=AvailabilityStatus(data["availability_status"])
            if data.get("availability_status")
            else AvailabilityStatus.IN_PRINT,
        )


class ReleaseTrack(CatalogueModel):
    id: str
    version: VersionRef
    track_number: int
    disc_number: int = 1
    side: Optional[str] = None
    release: Optional[Release] = None
    is_hidden: bool = False
    identifiers: Optional[List[Dict[str, Any]]] = None
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
            is_hidden=data.get("is_hidden_track"),
            identifiers=data.get("identifiers"),
            notes=data.get("notes"),
        )
