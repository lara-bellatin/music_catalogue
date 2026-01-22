import uuid
from datetime import date

import pytest

from music_catalogue.models.exceptions import ValidationError
from music_catalogue.models.works import (
    AudioChannel,
    AvailabilityStatus,
    CompletenessLevel,
    Credit,
    Genre,
    MediumType,
    Release,
    ReleaseCategory,
    ReleaseMediaItem,
    ReleaseStage,
    ReleaseTrack,
    Version,
    VersionType,
    Work,
    WorkCreate,
    WorkCreditCreate,
    WorkVersionCreate,
)


class TestGenre:
    """Test the Genre model"""

    def test_genre_from_dict_full_payload(self):
        payload = {
            "genre_id": "genre-1",
            "name": "Classical",
            "description": "Art music tradition",
        }

        genre = Genre.from_dict(payload)

        assert genre.id == "genre-1"
        assert genre.name == "Classical"
        assert genre.description == "Art music tradition"

    def test_genre_from_dict_missing_required_field(self):
        payload = {"name": "Classical"}
        with pytest.raises(KeyError):
            Genre.from_dict(payload)


class TestWork:
    """Test the Work model"""

    def test_work_from_dict_minimal_payload(self):
        payload = {"work_id": "work-1", "title": "Test Work"}

        work = Work.from_dict(payload)

        assert work.id == "work-1"
        assert work.title == "Test Work"
        assert work.language is None
        assert work.versions == []
        assert work.genres == []
        assert work.credits == []

    def test_work_from_dict_populates_nested_collections(self):
        payload = {
            "work_id": "work-2",
            "title": "Work 2",
            "language": "en",
            "work_genres": [
                {"genres": {"genre_id": "genre-2", "name": "Solo", "description": None}},
            ],
            "credits": [
                {
                    "credit_id": "credit-1",
                    "role": "Composer",
                    "is_primary": True,
                    "artist": {
                        "artist_id": "artist-7",
                        "artist_type": "solo",
                        "display_name": "Test Composer",
                    },
                    "person": {
                        "person_id": "person-3",
                        "legal_name": "Composer Name",
                    },
                }
            ],
        }

        work = Work.from_dict(payload)

        assert work.language == "en"
        assert len(work.genres) == 1
        assert work.genres[0].id == "genre-2"
        assert len(work.credits) == 1
        assert work.credits[0].role == "Composer"
        assert work.credits[0].is_primary is True
        assert work.credits[0].artist is not None
        assert work.credits[0].person is not None

    def test_work_from_dict_missing_required_field(self):
        payload = {"title": "No ID Work"}
        with pytest.raises(KeyError):
            Work.from_dict(payload)


class TestVersion:
    """Test the Version model"""

    def test_version_from_dict_full_payload(self):
        payload = {
            "version_id": "version-1",
            "work": {"work_id": "work-1", "title": "Symphony"},
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


class TestRelease:
    """Test the Release, ReleaseMediaItem and ReleaseTrack models"""

    def test_release_from_dict_full_payload(self):
        payload = {
            "release_id": "release-1",
            "title": "Live Album",
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
                "work": {"work_id": "work-9", "title": "Piece"},
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
            "is_hidden": False,
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
        assert track.version.completeness_level is CompletenessLevel.COMPLETE

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


class TestCredit:
    """Test the Credit model"""

    def test_credit_from_dict_with_related_entities(self):
        payload = {
            "credit_id": "credit-99",
            "work": None,
            "version": None,
            "artist": {
                "artist_id": "artist-42",
                "artist_type": "solo",
                "display_name": "Featured Artist",
            },
            "person": {
                "person_id": "person-9",
                "legal_name": "Featured Person",
            },
            "role": "Vocals",
            "is_primary": True,
            "credit_order": 1,
            "instruments": ["Voice"],
            "notes": "Lead performance",
        }

        credit = Credit.from_dict(payload)

        assert credit.id == "credit-99"
        assert credit.role == "Vocals"
        assert credit.is_primary is True
        assert credit.credit_order == 1
        assert credit.instruments == ["Voice"]
        assert credit.notes == "Lead performance"
        assert credit.work is None
        assert credit.version is None
        assert credit.artist is not None and credit.artist.display_name == "Featured Artist"
        assert credit.person is not None and credit.person.legal_name == "Featured Person"

    def test_credit_from_dict_missing_required_field(self):
        payload = {"role": "Vocals"}
        with pytest.raises(KeyError):
            Credit.from_dict(payload)


class TestWorkCreditCreate:
    """Tests for WorkCreditCreate model."""

    def test_validate_with_person_id_success(self):
        credit = WorkCreditCreate(person_id=str(uuid.uuid4()), role="Composer")

        credit.validate()

    def test_validate_with_artist_id_success(self):
        credit = WorkCreditCreate(artist_id=str(uuid.uuid4()), role="Composer")

        credit.validate()

    def test_validate_missing_identifiers_raises(self):
        credit = WorkCreditCreate(role="Composer")

        with pytest.raises(ValidationError) as exc_info:
            credit.validate()

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_both_identifiers_raises(self):
        credit = WorkCreditCreate(
            person_id=str(uuid.uuid4()),
            artist_id=str(uuid.uuid4()),
            role="Composer",
        )

        with pytest.raises(ValidationError) as exc_info:
            credit.validate()

        assert "Either person or artist ID" in str(exc_info.value)


class TestWorkVersionCreate:
    """Tests for WorkVersionCreate model."""

    def test_validate_success(self):
        version = WorkVersionCreate(
            title="A Work Version",
            primary_artist_id=str(uuid.uuid4()),
            version_type=VersionType.LIVE,
            release_year=1990,
            duration_seconds=480,
        )

        version.validate()

    def test_validate_invalid_primary_artist_uuid_raises(self):
        version = WorkVersionCreate(
            title="Invalid Artist",
            primary_artist_id="not-a-uuid",
        )

        with pytest.raises(ValidationError) as exc_info:
            version.validate()

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_release_year_raises(self):
        version = WorkVersionCreate(
            title="Impossible Year",
            primary_artist_id=str(uuid.uuid4()),
            release_year=1234567890,
        )

        with pytest.raises(ValidationError) as exc_info:
            version.validate()

        assert "Invalid year" in str(exc_info.value)


class TestWorkCreate:
    """Tests for WorkCreate model."""

    def test_validate_success(self):
        work = WorkCreate(
            title="A Work",
            origin_year_start=1900,
            origin_year_end=1950,
            genre_ids=[str(uuid.uuid4())],
            credits=[WorkCreditCreate(person_id=str(uuid.uuid4()), role="Composer")],
            versions=[
                WorkVersionCreate(
                    title="A Version",
                    primary_artist_id=str(uuid.uuid4()),
                    version_type=VersionType.ORIGINAL,
                )
            ],
        )

        work.validate()

    def test_validate_invalid_year_range_raises(self):
        work = WorkCreate(title="Invalid Years", origin_year_start=2000, origin_year_end=1990)

        with pytest.raises(ValidationError) as exc_info:
            work.validate()

        assert "Start year" in str(exc_info.value)

    def test_validate_invalid_credit_raises(self):
        work = WorkCreate(title="Missing Credit IDs", credits=[WorkCreditCreate(role="Composer")])

        with pytest.raises(ValidationError) as exc_info:
            work.validate()

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_invalid_genre_id_raises(self):
        work = WorkCreate(title="Invalid Genre ID", genre_ids=["not-a-uuid"])

        with pytest.raises(ValidationError) as exc_info:
            work.validate()

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_version_propagates(self):
        work = WorkCreate(
            title="Invalid Version",
            versions=[WorkVersionCreate(title="Broken", primary_artist_id="not-a-uuid")],
        )

        with pytest.raises(ValidationError) as exc_info:
            work.validate()

        assert "Invalid UUID" in str(exc_info.value)
