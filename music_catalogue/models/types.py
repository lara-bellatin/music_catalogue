from enum import Enum


class EntityType(str, Enum):
    PERSON = "person"
    ARTIST = "artist"
    WORK = "work"
    VERSION = "version"
    RELEASE = "release"
    MEDIA_ITEM = "media_item"
    CREDIT = "credit"
    GENRE = "genre"


class ArtistType(str, Enum):
    SOLO = "solo"
    GROUP = "group"


class AssetType(str, Enum):
    MEI = "mei"
    SCORE_IMAGE = "score_image"
    LEAD_SHEET = "lead_sheet"
    LYRICS = "lyrics"
    OTHER = "other"


class CollectionItemOwnerType(str, Enum):
    INSTITUTION = "institution"
    COLLECTOR = "collector"


class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserRole(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"


class VersionType(str, Enum):
    ORIGINAL = "original"
    COVER = "cover"
    REMIX = "remix"
    LIVE = "live"
    MASHUP = "mashup"
    DEMO = "demo"
    RADIO_EDIT = "radio_edit"
    OTHER = "other"


class CompletenessLevel(str, Enum):
    SPARSE = "sparse"
    PARTIAL = "partial"
    COMPLETE = "complete"


class ReleaseCategory(str, Enum):
    SINGLE = "single"
    EP = "ep"
    ALBUM = "album"
    COMPILATION = "compilation"
    LIVE = "live"
    SOUNDTRACK = "soundtrack"
    DELUXE = "deluxe"
    OTHER = "other"


class ReleaseStage(str, Enum):
    INITIAL = "initial"
    REISSUE = "reissue"
    REMASTER = "remaster"
    ANNIVERSARY = "anniversary"
    OTHER = "other"


class MediumType(str, Enum):
    DIGITAL = "digital"
    PHYSICAL = "physical"


class AudioChannel(str, Enum):
    MONO = "mono"
    STEREO = "stereo"
    SURROUND = "surround"
    DOLBY_ATMOS = "dolby_atmos"


class AvailabilityStatus(str, Enum):
    IN_PRINT = "in_print"
    LIMITED = "limited"
    OUT_OF_PRINT = "out_of_print"
    DIGITAL_ONLY = "digital_only"
