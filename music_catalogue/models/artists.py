from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import date
from enum import Enum


class ArtistType(str, Enum):
    SOLO = "solo"
    GROUP = "group"


class Person(BaseModel):
    id: str
    legal_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    pronouns: Optional[str] = None
    notes: Optional[str] = None


class Artist(BaseModel):
    id: str
    person: Optional[Person] = None
    artist_type: ArtistType
    display_name: str
    sort_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    identifiers: Optional[Any] = None
    members: Optional[List["ArtistMembership"]] = None


class ArtistMembership(BaseModel):
    id: str
    artist: Artist
    person: Person
    role: str
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None



Artist.model_rebuild()
ArtistMembership.model_rebuild()