from datetime import date
from typing import Optional

from pydantic import BaseModel

from music_catalogue.models.responses.users import User
from music_catalogue.models.responses.works import ReleaseMediaItem
from music_catalogue.models.types import AssetType, CollectionItemOwnerType, EntityType


class ExternalLink(BaseModel):
    id: str
    entity_type: EntityType
    entity_id: str
    label: str
    url: str
    added_by: User
    created_at: date
    source_verified: bool = False


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
    media_item: ReleaseMediaItem
    location: Optional[str] = None
    condition_grade: Optional[str] = None
    acquisition_date: Optional[date] = None
    notes: Optional[str] = None
