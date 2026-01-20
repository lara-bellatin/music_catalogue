from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from music_catalogue.models.users import User
from music_catalogue.models.utils import AnyEntityType, EntityType
from music_catalogue.models.works import ReleaseMediaItem


class AssetType(str, Enum):
    MEI = "mei"
    SCORE_IMAGE = "score_image"
    LEAD_SHEET = "lead_sheet"
    LYRICS = "lyrics"
    OTHER = "other"


class CollectionItemOwnerType(str, Enum):
    INSTITUTION = "institution"
    COLLECTOR = "collector"


class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExternalLink(BaseModel):
    id: str
    entity_type: EntityType
    entity: AnyEntityType
    label: str
    url: str
    added_by: User
    created_at: date
    source_verified: bool = False


class Evidence(BaseModel):
    id: str
    entity_type: EntityType
    entity: AnyEntityType
    uploaded_by: User
    source_type: str
    source_detail: str
    file_url: str
    created_at: date
    verified: bool = False


class NotationAsset(BaseModel):
    id: str
    entity_type: EntityType
    entity: AnyEntityType
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
