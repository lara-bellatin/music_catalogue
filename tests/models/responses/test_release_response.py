from datetime import date

import pytest

from music_catalogue.models.responses.releases import (
    Release,
    ReleaseMediaItem,
    ReleaseTrack,
)
from music_catalogue.models.types import (
    AudioChannel,
    AvailabilityStatus,
    MediumType,
    ReleaseCategory,
    ReleaseStage,
    VersionType,
)


class TestRelease:
    """Test the Release, ReleaseMediaItem and ReleaseTrack models"""

    def test_release_from_dict_full_payload(self):
        payload = {
            "release_id": "release-1",
            "release_title": "Live Album",
            "release_date": "2020-01-01",
            "release_category": "album",
            "catalog_number": "ABC-123",
            "publisher_number": "PUB-001",
            "label": "Great Records",
            "region": "US",
            "release_stage": "initial",
            "cover_art_url": "https://example.com/cover.jpg",
            "total_discs": 2,
            "total_tracks": 18,
            "notes": "Deluxe edition",
            "release_media_items": None,
        }

        release = Release.from_dict(payload)

        assert release.id == "release-1"
        assert release.title == "Live Album"
        assert release.release_date == date(2020, 1, 1)
        assert release.release_category is ReleaseCategory.ALBUM
        assert release.release_stage is ReleaseStage.INITIAL
        assert release.total_discs == 2
        assert release.total_tracks == 18
        assert release.media_items == []

    def test_release_media_item_from_dict_full_payload(self):
        payload = {
            "media_item_id": "media-1",
            "release": None,
            "medium_type": "digital",
            "format_name": "FLAC",
            "platform_or_vendor": "Bandcamp",
            "bitrate_kbps": 1411,
            "sample_rate_hz": 44100,
            "bit_depth": 16,
            "rpm": None,
            "channels": "stereo",
            "packaging": None,
            "accessories": None,
            "pressing_details": None,
            "sku": "SKU123",
            "barcode": "0123456789012",
            "catalog_variation": None,
            "availability_status": "in_print",
            "notes": "Lossless download",
        }

        media_item = ReleaseMediaItem.from_dict(payload)

        assert media_item.id == "media-1"
        assert media_item.medium_type is MediumType.DIGITAL
        assert media_item.format_name == "FLAC"
        assert media_item.platform_or_vendor == "Bandcamp"
        assert media_item.channels is AudioChannel.STEREO
        assert media_item.availability_status is AvailabilityStatus.IN_PRINT
        assert media_item.release is None

    def test_release_track_from_dict_full_payload(self):
        payload = {
            "release_track_id": "track-1",
            "release": None,
            "version": {
                "version_id": "version-2",
                "work": {"work_id": "work-9", "title": "Piece", "language": "en"},
                "title": "Piece (Demo)",
                "version_type": "demo",
                "primary_artist": {
                    "artist_id": "artist-2",
                    "artist_type": "solo",
                    "display_name": "Artist",
                },
                "completeness_level": "complete",
            },
            "track_number": 1,
            "disc_number": 1,
            "side": "A",
            "is_hidden_track": False,
            "notes": "Opener",
        }

        track = ReleaseTrack.from_dict(payload)

        assert track.id == "track-1"
        assert track.track_number == 1
        assert track.disc_number == 1
        assert track.side == "A"
        assert track.is_hidden is False
        assert track.version is not None
        assert track.version.id == "version-2"
        assert track.version.work is not None and track.version.work.id == "work-9"
        assert track.version.version_type is VersionType.DEMO

    def test_release_from_dict_missing_required_field(self):
        payload = {"title": "Unnamed Release"}
        with pytest.raises(KeyError):
            Release.from_dict(payload)

    def test_release_media_item_from_dict_missing_required_field(self):
        payload = {"format_name": "FLAC"}
        with pytest.raises(KeyError):
            ReleaseMediaItem.from_dict(payload)

    def test_release_track_from_dict_missing_required_field(self):
        payload = {"track_number": 1}
        with pytest.raises(KeyError):
            ReleaseTrack.from_dict(payload)
