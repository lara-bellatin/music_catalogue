from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Union

from pydantic import BaseModel

if TYPE_CHECKING:
    from music_catalogue.models.artists import Artist, Person
    from music_catalogue.models.works import Credit, Genre, Release, ReleaseMediaItem, Version, Work


class EntityType(str, Enum):
    PERSON = "person"
    ARTIST = "artist"
    WORK = "work"
    VERSION = "version"
    RELEASE = "release"
    MEDIA_ITEM = "media_item"
    CREDIT = "credit"
    GENRE = "genre"


type AnyEntityType = Union[Person, Artist, Work, Version, Release, ReleaseMediaItem, Credit, Genre]


class UnifiedSearchResult(BaseModel):
    entity_type: EntityType
    entity_id: str
    display_text: str
    rank: float

    @classmethod
    def from_dict(cls, data: Dict) -> "UnifiedSearchResult":
        return cls(
            entity_type=EntityType(data["entity_type"]),
            entity_id=data["entity_id"],
            display_text=data["display_text"],
            rank=data["rank"],
        )


def _parse(model_cls: BaseModel, data: Dict) -> AnyEntityType:
    if not data:
        return None
    return model_cls.from_dict(data)


def _parse_list(model_cls: BaseModel, data: Dict) -> List[AnyEntityType]:
    if not data:
        return []
    return [_parse(model_cls, item) for item in data if _parse(model_cls, item) is not None]
