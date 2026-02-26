"""Fetch a Spotify album and import artists, tracks, and release into the catalogue database."""

import argparse
import asyncio
import base64
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, TypedDict

from dotenv import load_dotenv
from pydantic import Field

from music_catalogue.models.inputs.artist_create import ArtistCreate
from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.inputs.credit_create import WorkVersionCreditCreate
from music_catalogue.models.inputs.person_create import PersonCreate
from music_catalogue.models.inputs.release_create import ReleaseCreate, ReleaseTrackCreate
from music_catalogue.models.inputs.version_create import VersionCreate
from music_catalogue.models.inputs.work_create import WorkCreate, WorkVersionCreate
from music_catalogue.models.responses.artists import Artist
from music_catalogue.models.responses.persons import Person
from music_catalogue.models.responses.releases import Release
from music_catalogue.models.responses.versions import Version
from music_catalogue.models.responses.works import Work
from music_catalogue.models.types import ArtistType, ReleaseCategory, VersionType

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_spotify_token() -> str:
    """Authenticate via Client Credentials flow and return an access token."""
    url = "https://accounts.spotify.com/api/token"
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    credentials = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode())
    return body["access_token"]


def spotify_get(path: str, token: str) -> Dict[str, Any]:
    """GET helper for the Spotify Web API."""
    url = f"https://api.spotify.com/v1/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


class ExtractedArtist(TypedDict):
    spotify_id: str
    name: str
    url: str


class ExtractedTrack(TypedDict):
    spotify_id: str
    title: str
    disc_number: int
    track_number: int
    duration_seconds: int
    explicit: bool
    url: str
    genres: List[str] = Field(default_factory=List)
    external_ids: Dict[str, str] = Field(default_factory=Dict)
    artists: List[ExtractedArtist] = Field(default_factory=List)


class ExtractedAlbumData(TypedDict):
    spotify_id: str
    title: str
    release_date: Optional[str] = None
    release_category: str
    label: Optional[str] = None
    cover_art_url: Optional[str] = None
    total_tracks: int
    url: str
    external_ids: Dict[str, str] = Field(default_factory=Dict)
    artists: List[ExtractedArtist] = Field(default_factory=List)
    tracks: List[ExtractedTrack] = Field(default_factory=List)


def _map_album_type(album_type: str) -> str:
    """Map Spotify album_type to catalogue ReleaseCategory value."""
    mapping = {
        "album": ReleaseCategory.ALBUM,
        "single": ReleaseCategory.SINGLE,
        "compilation": ReleaseCategory.COMPILATION,
    }
    return mapping.get(album_type, ReleaseCategory.ALBUM)


def extract_album_data(album_id: str, token: str) -> ExtractedAlbumData:
    """Fetch album, artist, and track data from Spotify and return a structured dict."""
    album = spotify_get(f"albums/{album_id}", token)

    # Collect unique album-level artists
    album_artists: List[ExtractedArtist] = []
    for artist in album.get("artists", []):
        album_artists.append(
            ExtractedArtist(
                spotify_id=artist["id"],
                name=artist["name"],
                url=artist["external_urls"]["spotify"],
            )
        )

    # Collect tracks
    tracks: List[ExtractedTrack] = []
    for track in album.get("tracks", {}).get("items", []):
        track_info = spotify_get(f"tracks/{track['id']}", token)
        track_artists: List[ExtractedArtist] = [
            ExtractedArtist(
                spotify_id=ta["id"],
                name=ta["name"],
                url=ta["external_urls"]["spotify"],
            )
            for ta in track.get("artists", [])
        ]
        tracks.append(
            ExtractedTrack(
                spotify_id=track["id"],
                title=track["name"],
                disc_number=track.get("disc_number", 1),
                track_number=track.get("track_number", 1),
                duration_seconds=track["duration_ms"] // 1000,
                explicit=track.get("explicit", False),
                url=track["external_urls"]["spotify"],
                external_ids=track_info.get("external_ids"),
                artists=track_artists,
            )
        )

    # Use the largest cover art image for best resolution
    images = album.get("images", [])
    cover_art_url = images[0]["url"] if images else None

    return ExtractedAlbumData(
        spotify_id=album["id"],
        title=album["name"],
        release_date=album.get("release_date"),
        release_category=_map_album_type(album.get("album_type", "album")),
        label=album.get("label"),
        cover_art_url=cover_art_url,
        total_tracks=album.get("total_tracks", len(tracks)),
        url=album["external_urls"]["spotify"],
        external_ids=album.get("external_ids"),
        artists=album_artists,
        tracks=tracks,
    )


async def find_or_create_person(name: str) -> Person:
    """Return an existing person matching specified name, or create a new one."""
    matches = await Person.search(name)
    if matches:
        print(f"Found person match by name: {matches[0].id}")
        # search returns PersonRef object, need to return full Person
        return await Person.get_by_id(matches[0].id)
    person = await Person.create(PersonCreate(legal_name=name))
    print(f"Created person: {person.id}")
    return person


async def find_or_create_artist(artist_info: ExtractedArtist) -> Artist:
    """Return an existing artist (by Spotify identifier or name) or create a new one."""
    # Try to get by identifiers
    artist = await Artist.get_by_identifier(identifier_label="spotify", identifier_value=artist_info["spotify_id"])
    if artist:
        print(f"Found artist by identifier: {artist.id}")
        return artist

    # Try to get by name search
    matches = await Artist.search(artist_info["name"])
    if matches:
        print(f"Found artist match by name: {matches[0].id}")
        return await Artist.get_by_id(matches[0].id)

    # Try to get person by name search or create
    person = await find_or_create_person(artist_info["name"])

    # If not found, create
    new_artist = await Artist.create(
        ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name=artist_info["name"],
            sort_name=artist_info["name"],
            person_id=person.id,
            identifiers=[{"label": "spotify", "value": artist_info["spotify_id"]}],
            external_links=[ExternalLinkCreate(label="Spotify", url=artist_info["url"], source_verified=True)],
        )
    )
    print(f"Created artist: {new_artist.id}")
    return new_artist


async def find_or_create_version(track: ExtractedTrack, artist_id_map: Dict[str, str]) -> Version:
    """Return an existing version (by Spotify identifier or title) or create a new one."""
    # Try to get by identifiers
    version = await Version.get_by_identifier(identifier_label="spotify", identifier_value=track["spotify_id"])
    if version:
        print(f"Found version by identifier: {version.id}")
        return version

    # Try to get by title search
    matches = await Version.search(track["title"])
    if matches:
        print(f"Found version match by name: {matches[0].id}")
        return await Version.get_by_id(matches[0].id)

    # Try to get a work match by search, removing anything after symbols
    work_matches = await Work.search(track["title"].split("-")[0].split("(")[0].strip())
    if work_matches:
        print(f"Found work match by name: {work_matches[0].id}")
        # Create version with found work ID
        version = await Version.create(
            VersionCreate(
                work_id=work_matches[0].id,
                title=track["title"],
                primary_artist_id=artist_id_map.get(track["artists"][0]["spotify_id"]),
                duration_seconds=track["duration_seconds"],
                version_type=VersionType.ORIGINAL,
                identifiers=[{"label": "spotify", "value": track["spotify_id"]}]
                + [{"label": k, "value": v} for k, v in (track.get("external_ids") or {}).items()],
                external_links=[ExternalLinkCreate(label="Spotify", url=track["url"], source_verified=True)],
                credits=[
                    WorkVersionCreditCreate(
                        artist_id=artist_id_map.get(artist["spotify_id"]),
                        role="performer",
                        is_primary=(artist["spotify_id"] == track["artists"][0]["spotify_id"]),
                    )
                    for artist in track["artists"]
                ],
            )
        )
        print(f"Created version: {version.id}")
        return version

    # If not found, create a new work and version
    work = await Work.create(
        WorkCreate(
            title=track["title"],
            versions=[
                WorkVersionCreate(
                    title=track["title"],
                    primary_artist_id=artist_id_map.get(track["artists"][0]["spotify_id"]),
                    duration_seconds=track["duration_seconds"],
                    version_type=VersionType.ORIGINAL,
                    identifiers=[{"label": "spotify", "value": track["spotify_id"]}]
                    + [{"label": k, "value": v} for k, v in (track.get("external_ids") or {}).items()],
                    external_links=[ExternalLinkCreate(label="Spotify", url=track["url"], source_verified=True)],
                    credits=[
                        WorkVersionCreditCreate(
                            artist_id=artist_id_map.get(artist["spotify_id"]),
                            role="performer",
                            is_primary=(artist["spotify_id"] == track["artists"][0]["spotify_id"]),
                        )
                        for artist in track["artists"]
                    ],
                )
            ],
        )
    )
    print(f"Created work: {work.id}")
    print(f"Created version: {work.versions[0].id}")

    # Return the version, not the work
    return work.versions[0]


async def create_release(
    album_data: ExtractedAlbumData,
    version_map: Dict[str, str],
    artist_id_map: Dict[str, str],
) -> str:
    """Insert a release and its release_tracks."""
    album_artists = album_data["artists"]
    primary_artist_id = artist_id_map.get(album_artists[0]["spotify_id"]) if album_artists else None

    return await Release.create(
        ReleaseCreate(
            release_title=album_data["title"],
            release_date=album_data["release_date"],
            release_category=album_data["release_category"],
            label=album_data.get("label"),
            cover_art_url=album_data.get("cover_art_url"),
            total_tracks=album_data["total_tracks"],
            primary_artist_id=primary_artist_id,
            tracks=[
                ReleaseTrackCreate(
                    version_id=version_map.get(track["spotify_id"], None),
                    disc_number=track["disc_number"],
                    track_number=track["track_number"],
                    identifiers=[{"label": "spotify", "value": track["spotify_id"]}]
                    + [{"label": k, "value": v} for k, v in (track.get("external_ids") or {}).items()],
                )
                for track in album_data["tracks"]
            ],
            identifiers=[{"label": "spotify", "value": album_data["spotify_id"]}]
            + [{"label": k, "value": v} for k, v in (album_data.get("external_ids") or {}).items()],
            external_links=[ExternalLinkCreate(label="Spotify", url=album_data["url"], source_verified=True)],
            credits=[
                WorkVersionCreditCreate(
                    artist_id=artist_id_map.get(artist["spotify_id"]),
                    role="performer",
                    is_primary=(artist["spotify_id"] == primary_artist_id),
                    credit_order=i,
                )
                for i, artist in enumerate(album_artists)
            ],
        ),
    )


async def add_to_database(data: ExtractedAlbumData) -> str:
    """Create all entities in the database and return the release_id."""
    # Resolve all unique artists across the album (album-level + track-level)
    all_artists: Dict[str, ExtractedArtist] = {}
    for a in data["artists"]:
        all_artists[a["spotify_id"]] = a
    for track in data["tracks"]:
        for a in track["artists"]:
            all_artists[a["spotify_id"]] = a

    # Create persons + artists
    artist_id_map: Dict[str, str] = {}  # spotify_id -> catalogue artist_id
    for spotify_id, artist_info in all_artists.items():
        artist = await find_or_create_artist(artist_info)
        artist_id_map[spotify_id] = artist.id

    # Create versions (tracks) and collect version IDs
    version_map: Dict[str, str] = {}  # spotify_track_id -> catalogue version_id
    for track in data["tracks"]:
        version = await find_or_create_version(track, artist_id_map)
        version_map[track["spotify_id"]] = version.id

    # Create the release and link tracks
    return await create_release(data, version_map, artist_id_map)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Import a Spotify album into the catalogue database")
    parser.add_argument("album_id", help="Spotify album ID")
    parser.add_argument("--save", action="store_true", help="Actually write to the database (default: preview only)")
    args = parser.parse_args()

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env")
        return

    print("Authenticating with Spotify...")
    token = get_spotify_token()

    print(f"Fetching album {args.album_id}...")
    album_data = extract_album_data(args.album_id, token)

    print("\nExtracted Data:")
    print(json.dumps(album_data, ensure_ascii=False, indent=2))

    if args.save:
        print("\nAdding to Database...")
        release_id = await add_to_database(album_data)
        print(f"Release created with ID: {release_id}")
    else:
        print("\nDry run complete. Use --save to write to the database.")


if __name__ == "__main__":
    asyncio.run(main())
