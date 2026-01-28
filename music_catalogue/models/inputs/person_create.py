from typing import Optional

from pydantic import BaseModel, model_validator

from music_catalogue.models.validation import validate_start_and_end_dates


class PersonCreate(BaseModel):
    legal_name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    pronouns: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        validate_start_and_end_dates(self.birth_date, self.death_date)
