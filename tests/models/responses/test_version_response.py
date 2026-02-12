from datetime import date

import pytest

from music_catalogue.models.responses.versions import Version
from music_catalogue.models.types import (
    CompletenessLevel,
    VersionType,
)


class TestVersion:
    """Test the Version model"""

    def test_version_from_dict_full_payload(self):
        payload = {
            "version_id": "version-1",
            "work": {"work_id": "work-1", "title": "Symphony", "language": "en"},
            "title": "Symphony (Live)",
            "version_type": "live",
            "based_on_version": None,
            "primary_artist": {
                "artist_id": "artist-1",
                "artist_type": "solo",
                "display_name": "Performer",
            },
            "release_date": "2020-01-01",
            "release_year": 2020,
            "duration_seconds": 600,
            "bpm": 120,
            "key_signature": "C minor",
            "lyrics_reference": None,
            "completeness_level": "complete",
            "notes": "Recorded at venue",
        }

        version = Version.from_dict(payload)

        assert version.id == "version-1"
        assert version.title == "Symphony (Live)"
        assert version.work is not None and version.work.id == "work-1"
        assert version.version_type is VersionType.LIVE
        assert version.release_date == date(2020, 1, 1)
        assert version.release_year == 2020
        assert version.duration_seconds == 600
        assert version.primary_artist is not None and version.primary_artist.id == "artist-1"
        assert version.completeness_level is CompletenessLevel.COMPLETE
        assert version.notes == "Recorded at venue"

    def test_version_from_dict_missing_required_field(self):
        payload = {
            "title": "Incomplete Version",
            "version_type": "live",
            "completeness_level": "complete",
        }
        with pytest.raises(KeyError):
            Version.from_dict(payload)
