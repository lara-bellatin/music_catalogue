from datetime import date
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.responses.assets import ExternalLink
from music_catalogue.models.responses.references import ArtistRef, CreditRef, PersonRef
from music_catalogue.models.types import EntityType
from music_catalogue.models.utils import _parse, _parse_list


class PersonArtistMembership(BaseModel):
    id: str
    artist: Optional[ArtistRef] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonArtistMembership":
        return cls(
            id=data["membership_id"],
            artist=_parse(ArtistRef, data.get("artist")),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            role=data.get("role"),
            notes=data.get("notes"),
        )


class Person(CatalogueModel):
    table_name: ClassVar[str] = "persons"
    pk_column: ClassVar[str] = "person_id"
    entity_type: ClassVar[EntityType] = EntityType.PERSON
    ref_model: ClassVar[BaseModel] = PersonRef
    query: ClassVar[str] = f"""
        person_id,
        legal_name,
        birth_date,
        death_date,
        pronouns,
        identifiers,
        notes,
        artist:artists({ArtistRef.query}),
        artist_memberships(
            membership_id,
            start_year,
            end_year,
            role,
            notes,
            artist:artists({ArtistRef.query})
        ),
        credits({CreditRef.artist_person_query})
    """

    id: str
    legal_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    pronouns: Optional[str] = None
    identifiers: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    credits: List[CreditRef] = Field(default_factory=list)
    memberships: Optional[List[PersonArtistMembership]] = None
    external_links: Optional[List[ExternalLink]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Person":
        return cls(
            id=data["person_id"],
            legal_name=data["legal_name"],
            birth_date=date.fromisoformat(data.get("birth_date")) if data.get("birth_date") else None,
            death_date=date.fromisoformat(data.get("death_date")) if data.get("death_date") else None,
            pronouns=data.get("pronouns"),
            identifiers=data.get("identifiers"),
            notes=data.get("notes"),
            credits=_parse_list(CreditRef, data.get("credits")),
            memberships=_parse_list(PersonArtistMembership, data.get("artist_memberships")) or None,
        )
