from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from music_catalogue.models.exceptions import APIError
from music_catalogue.models.responses.releases import Release
from music_catalogue.models.responses.works import Work

router = APIRouter(prefix="/extract", tags=["Extract"])


class CNWExtractRequest(BaseModel):
    source: str


class SpotifyAlbumExtractRequest(BaseModel):
    album_id: str


@router.post("/cnw", response_model=Work, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED)
async def extract_cnw(body: CNWExtractRequest):
    """
    Extract a work from a Carl Nielsen Works MEI XML document and add it to the database.
    """
    from scripts.cnw_xml_to_db import add_to_database, transform_mei

    try:
        extracted_data = transform_mei(body.source)
        return await add_to_database(extracted_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to extract CNW data: {str(e)}"
        )
    except:
        raise


@router.post(
    "/spotify-album", response_model=Release, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED
)
async def extract_spotify_album(body: SpotifyAlbumExtractRequest):
    """
    Extract album, track, and artist data from Spotify and add it to the database.
    """
    from scripts.spotify_album_to_db import (
        SPOTIFY_CLIENT_ID,
        SPOTIFY_CLIENT_SECRET,
        add_to_database,
        extract_album_data,
        get_spotify_token,
    )

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env",
        )

    try:
        token = get_spotify_token()
        album_data = extract_album_data(body.album_id, token)
        return await add_to_database(album_data)
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract Spotify album data: {str(e)}",
        )
    except:
        raise
