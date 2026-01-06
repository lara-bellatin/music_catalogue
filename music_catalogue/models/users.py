from pydantic import BaseModel
from typing import Optional, Union
from datetime import date
from enum import Enum

from music_catalogue.models.artists import Person, Artist
from music_catalogue.models.works import Work, Version, Release, ReleaseMediaItem, Credit, Genre


class UserRole(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"


class EntityType(str, Enum):
    PERSON = "person"
    ARTIST = "artist"
    WORK = "work"
    VERSION = "version"
    RELEASE = "release"
    MEDIA_ITEM = "media_item"
    CREDIT = "credit"


class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(BaseModel):
    id: str
    display_name: str
    email: str
    trust_score: int
    role: UserRole = UserRole.MEMBER

class Tag(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class TagAssignment(BaseModel):
    id: str
    tag: Tag
    entity_type: EntityType
    entity: Union[Person, Artist, Work, Version, Release, ReleaseMediaItem, Credit, Genre]
    user: User
    confidence: int
    created_at: date


class Contribution(BaseModel):
    id: str
    entity_type: EntityType
    entity: Union[Person, Artist, Work, Version, Release, ReleaseMediaItem, Credit, Genre]
    user: User
    change_summary: str
    contribution_status: ContributionStatus
    created_at: date
    reviewed_by: Optional[User] = None