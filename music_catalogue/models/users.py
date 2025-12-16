from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import date
from enum import Enum


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

# MISSING
# class TagAssignment
# class Contributions