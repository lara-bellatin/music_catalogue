import asyncio
import os
from dotenv import load_dotenv
from supabase import create_async_client, AsyncClient

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: AsyncClient | None = None
_lock = asyncio.Lock()

async def get_supabase() -> AsyncClient:
    global supabase
    if supabase:
        return supabase
    async with _lock:
        if not supabase:
            supabase = await create_async_client(
                SUPABASE_URL,
                SUPABASE_KEY,
            )
    
    return supabase
