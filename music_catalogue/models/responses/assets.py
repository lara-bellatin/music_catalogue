from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel

from music_catalogue.models.responses.references import ReleaseMediaItemRef
from music_catalogue.models.responses.users import User
from music_catalogue.models.types import AssetType, CollectionItemOwnerType, EntityType


class ExternalLink(BaseModel):
    label: str
    url: str
    added_by: Optional[User] = None
    created_at: Optional[date] = None
    source_verified: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "ExternalLink":
        return cls(
            label=data["label"],
            url=data["url"],
            source_verified=data["source_verified"],
        )


class Evidence(BaseModel):
    id: str
    entity_type: EntityType
    entity_id: str
    uploaded_by: User
    source_type: str
    source_detail: str
    file_url: str
    created_at: date
    verified: bool = False


class NotationAsset(BaseModel):
    id: str
    entity_type: EntityType
    entity_id: str
    asset_type: AssetType
    file_url: str
    uploaded_by: User
    created_at: date
    mime_type: Optional[str] = None


class CollectionItem(BaseModel):
    id: str
    owner_type: CollectionItemOwnerType
    owner_name: str
    media_item: ReleaseMediaItemRef
    location: Optional[str] = None
    condition_grade: Optional[str] = None
    acquisition_date: Optional[date] = None
    notes: Optional[str] = None
