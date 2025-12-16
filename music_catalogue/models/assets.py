from pydantic import BaseModel
from typing import Any, List, Optional
from datetime import date
from enum import Enum


class AssetType(str, Enum):
    MEI = "mei"
    SCORE_IMAGE = "score_image"
    LEAD_SHEET = "lead_sheet"
    LYRICS = "lyrics"
    OTHER = "other"


class CollectionItemOwnerType(str, Enum):
    INSTITUTION = "institution"
    COLLECTOR = "collector"

# MISSING
# class ExternalLinks
# class Evidence
# class NotationAssets
# class CollectionItems