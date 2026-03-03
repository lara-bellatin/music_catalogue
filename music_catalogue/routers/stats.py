import asyncio

from fastapi import APIRouter, HTTPException, status

from music_catalogue.crud.supabase_client import get_supabase
from music_catalogue.models.responses.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["Stats"])

TABLES = ["works", "versions", "artists", "releases", "performances", "persons"]


async def _count(table: str) -> int:
    supabase = await get_supabase()
    res = await supabase.table(table).select("*", count="exact", head=True).execute()
    return res.count


@router.get("/", response_model=StatsResponse, status_code=status.HTTP_200_OK)
async def get_stats():
    """Returns entity counts for the catalogue."""
    try:
        counts = await asyncio.gather(*[_count(t) for t in TABLES])
        return StatsResponse(**dict(zip(TABLES, counts)))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}",
        )
