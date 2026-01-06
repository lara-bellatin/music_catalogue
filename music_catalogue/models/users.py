from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

from music_catalogue.models.utils import AnyEntityType, EntityType


class UserRole(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"


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
    entity: AnyEntityType
    user: User
    confidence: int
    created_at: date


class Contribution(BaseModel):
    id: str
    entity_type: EntityType
    entity: AnyEntityType
    user: User
    change_summary: str
    contribution_status: ContributionStatus
    created_at: date
    reviewed_by: Optional[User] = None