from pydantic import BaseModel


class StatsResponse(BaseModel):
    works: int
    versions: int
    artists: int
    releases: int
    performances: int
    persons: int
