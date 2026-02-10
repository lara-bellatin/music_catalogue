from typing import ClassVar, Dict, List, Optional

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.base import CatalogueModel
from music_catalogue.models.exceptions import APIError
from music_catalogue.models.inputs.artist_create import ArtistCreate
from music_catalogue.models.responses.references import CreditRef, PersonRef, VersionRef
from music_catalogue.models.types import ArtistType, EntityType
from music_catalogue.models.utils import _parse, _parse_list
from supabase import PostgrestAPIError


class Artist(CatalogueModel):
    table_name: ClassVar[str] = "artists"
    pk_column: ClassVar[str] = "artist_id"
    entity_type: ClassVar[EntityType] = EntityType.ARTIST
    query: ClassVar[str] = f"""
        artist_id,
        person:persons({PersonRef.query}),
        artist_type,
        display_name,
        sort_name,
        alternative_names,
        start_year,
        end_year,
        artist_memberships(
            membership_id,
            start_year,
            end_year,
            role,
            notes,
            person:persons({PersonRef.query})
        ),
        versions({VersionRef.query}),
        credits({CreditRef.artist_person_query})
    """

    id: str
    person: Optional[PersonRef] = None
    artist_type: ArtistType
    display_name: str
    sort_name: Optional[str] = None
    alternative_names: Optional[List[str]] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    members: Optional[List["ArtistMembership"]] = None
    credits: Optional[List[CreditRef]] = None
    versions: Optional[List[VersionRef]] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Artist":
        return cls(
            id=data["artist_id"],
            person=_parse(PersonRef, data.get("person")),
            artist_type=ArtistType(data["artist_type"]),
            display_name=data["display_name"],
            sort_name=data.get("sort_name"),
            alternative_names=data.get("alternative_names"),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            members=_parse_list(ArtistMembership, data.get("artist_memberships", None)) or None,
            credits=_parse_list(CreditRef, data.get("credits", None)) or None,
            versions=_parse_list(VersionRef, data.get("versions", None)) or None,
        )

    @classmethod
    async def create(cls, data: "ArtistCreate", exclude: set = None) -> "Artist":
        exclude = (exclude or set()) | {"members"}
        artist = None
        supabase = await get_supabase()

        try:
            artist = await super().create(data, exclude=exclude)

            if data.members:
                await (
                    supabase.table("artist_memberships")
                    .insert(
                        [{"group_id": artist.id, **member.model_dump(exclude_none=True)} for member in data.members]
                    )
                    .execute()
                )
                # Re-fetch to include memberships
                return await cls.get_by_id(artist.id)

            return artist

        except PostgrestAPIError as e:
            # Rollback on failure
            if artist and artist.id:
                await supabase.table("artist_memberships").delete().eq("group_id", artist.id).execute()
                await supabase.table("artists").delete().eq("artist_id", artist.id).execute()
            raise APIError(str(e)) from None


class ArtistMembership(CatalogueModel):
    id: str
    person: Optional[PersonRef] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    role: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtistMembership":
        return cls(
            id=data["membership_id"],
            person=_parse(PersonRef, data.get("person")),
            start_year=data.get("start_year"),
            end_year=data.get("end_year"),
            role=data.get("role"),
            notes=data.get("notes"),
        )
