from typing import Optional

from pydantic import BaseModel


class ExternalLinkCreate(BaseModel):
    label: str
    url: str
    source_verified: bool = False
    added_by_id: Optional[str] = None
