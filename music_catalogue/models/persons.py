from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel

from music_catalogue.models.utils import validate_start_and_end_dates


class Person(BaseModel):
    id: str
    legal_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    pronouns: Optional[str] = None
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Person":
        return cls(
            id=data["person_id"],
            legal_name=data["legal_name"],
            birth_date=date.fromisoformat(data.get("birth_date")) if data.get("birth_date") else None,
            death_date=date.fromisoformat(data.get("death_date")) if data.get("death_date") else None,
            pronouns=data.get("pronouns"),
            notes=data.get("notes"),
        )


class PersonCreate(BaseModel):
    legal_name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    pronouns: Optional[str] = None
    notes: Optional[str] = None

    def validate(self):
        validate_start_and_end_dates(self.birth_date, self.death_date)
