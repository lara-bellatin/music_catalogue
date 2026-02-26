from typing import List, Optional

from pydantic import BaseModel, model_validator


class CreditCreate(BaseModel):
    work_id: Optional[str] = None
    version_id: Optional[str] = None
    release_id: Optional[str] = None
    artist_id: Optional[str] = None
    person_id: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        # Check exactly one of person_id or artist_id
        if (not self.artist_id and not self.person_id) or (self.artist_id and self.person_id):
            raise ValueError("Either person or artist ID is required for credits")

        # Check exactly one of work_id, version_id, or release_id
        provided = sum(bool(x) for x in [self.work_id, self.version_id, self.release_id])
        if provided != 1:
            raise ValueError("Either work, version or release ID is required for credits")

        return self


class WorkVersionCreditCreate(BaseModel):
    artist_id: Optional[str] = None
    person_id: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        # Check exactly one of person_id or artist_id
        if (not self.artist_id and not self.person_id) or (self.artist_id and self.person_id):
            raise ValueError("Either person or artist ID is required for credits")

        return self


class PersonArtistCreditCreate(BaseModel):
    work_id: Optional[str] = None
    version_id: Optional[str] = None
    release_id: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False
    credit_order: Optional[int] = None
    instruments: Optional[List[str]] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate(self):
        # Check exactly one of work_id, version_id, or release_id
        provided = sum(bool(x) for x in [self.work_id, self.version_id, self.release_id])
        if provided != 1:
            raise ValueError("Either work, version or release ID is required for credits")

        return self
