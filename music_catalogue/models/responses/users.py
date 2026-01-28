from datetime import date
from typing import Optional

from pydantic import BaseModel

from music_catalogue.models.types import ContributionStatus, EntityType, UserRole


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
    entity_id: str
    user: User
    confidence: int
    created_at: date


class Contribution(BaseModel):
    id: str
    entity_type: EntityType
    entity_id: str
    user: User
    change_summary: str
    contribution_status: ContributionStatus
    created_at: date
    reviewed_by: Optional[User] = None
