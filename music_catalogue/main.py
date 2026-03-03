from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from music_catalogue.routers import (
    artists,
    extract,
    genres,
    performances,
    persons,
    releases,
    search,
    stats,
    versions,
    works,
)

app = FastAPI(title="Music Catalogue API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(artists.router)
app.include_router(persons.router)
app.include_router(works.router)
app.include_router(versions.router)
app.include_router(performances.router)
app.include_router(releases.router)
app.include_router(genres.router)
app.include_router(extract.router)
app.include_router(stats.router)
