from datetime import date, datetime
from typing import Dict, Optional

from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.responses.references import ReleaseMediaItemRef
from music_catalogue.models.responses.users import User
from music_catalogue.models.types import AssetType, CollectionItemOwnerType


class ExternalLink(CatalogueModel):
    table_name = "external_links"
    pk_column = "link_id"

    label: str
    url: str
    added_by: Optional[User] = None
    created_at: Optional[datetime] = None
    source_verified: bool = False

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            label=data["label"],
            url=data["url"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at", None) else None,
            source_verified=data["source_verified"],
        )


class Evidence(CatalogueModel):
    id: str
    uploaded_by: User
    source_type: str
    source_detail: str
    file_url: str
    created_at: datetime
    verified: bool = False


class NotationAsset(CatalogueModel):
    id: str
    asset_type: AssetType
    file_url: str
    uploaded_by: User
    created_at: datetime
    mime_type: Optional[str] = None


class CollectionItem(CatalogueModel):
    id: str
    owner_type: CollectionItemOwnerType
    owner_name: str
    media_item: ReleaseMediaItemRef
    location: Optional[str] = None
    condition_grade: Optional[str] = None
    acquisition_date: Optional[date] = None
    notes: Optional[str] = None
