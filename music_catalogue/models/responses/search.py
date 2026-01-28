from typing import Dict

from pydantic import BaseModel

from music_catalogue.models.types import EntityType


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
