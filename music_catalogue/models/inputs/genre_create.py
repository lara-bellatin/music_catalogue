from typing import Optional

from pydantic import BaseModel


class GenreCreate(BaseModel):
    name: str
    description: Optional[str] = None
