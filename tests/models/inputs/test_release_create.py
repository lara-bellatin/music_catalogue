from datetime import date

import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.release_create import (
    ReleaseCreate,
    ReleaseMediaItemCreate,
    ReleaseTrackCreate,
)


class TestReleaseMediaItemCreate:
    """Tests for ReleaseMediaItemCreate model."""

    def test_validate_minimal_success(self):
        ReleaseMediaItemCreate(
            medium_type="digital",
            format_name="FLAC",
        )

    def test_validate_full_success(self):
        ReleaseMediaItemCreate(
            medium_type="physical",
            format_name="Vinyl LP",
            platform_or_vendor="Amazon",
            bitrate_kbps=320,
            sample_rate_hz=44100,
            bit_depth=16,
            rpm=33.3,
            channels="stereo",
            packaging="Gatefold",
            accessories="Poster",
            pressing_details="180g",
            sku="SKU-123",
            barcode="1234567890",
            catalog_variation="Deluxe",
            availability_status="in_print",
            notes="Limited edition",
        )

    def test_validate_missing_required_medium_type_raises(self):
        with pytest.raises(ValidationError):
            ReleaseMediaItemCreate(format_name="FLAC")

    def test_validate_missing_required_format_name_raises(self):
        with pytest.raises(ValidationError):
            ReleaseMediaItemCreate(medium_type="digital")


class TestReleaseTrackCreate:
    """Tests for ReleaseTrackCreate model."""

    def test_validate_success(self, sample_uuid):
        ReleaseTrackCreate(
            version_id=sample_uuid,
            track_number=1,
        )

    def test_validate_full_success(self, sample_uuid):
        ReleaseTrackCreate(
            version_id=sample_uuid,
            track_number=3,
            disc_number=2,
            side="A",
            is_hidden=True,
            notes="Bonus track",
        )

    def test_validate_missing_version_id_raises(self):
        with pytest.raises(ValidationError):
            ReleaseTrackCreate(track_number=1)

    def test_validate_missing_track_number_raises(self, sample_uuid):
        with pytest.raises(ValidationError):
            ReleaseTrackCreate(version_id=sample_uuid)

    def test_validate_invalid_version_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ReleaseTrackCreate(version_id="not-a-uuid", track_number=1)

        assert "Invalid UUID" in str(exc_info.value)


class TestReleaseCreate:
    """Tests for ReleaseCreate model."""

    def test_validate_minimal_success(self):
        ReleaseCreate(title="Abbey Road")

    def test_validate_full_success(self, sample_uuid):
        ReleaseCreate(
            title="Abbey Road",
            release_date=date(1969, 9, 26),
            release_category="album",
            catalog_number="PCS 7088",
            publisher_number="PN-001",
            label="Apple Records",
            region="UK",
            release_stage="initial",
            cover_art_url="https://example.com/cover.jpg",
            total_discs=1,
            total_tracks=17,
            notes="Classic album",
            media_items=[
                ReleaseMediaItemCreate(
                    medium_type="physical",
                    format_name="Vinyl LP",
                ),
            ],
            tracks=[
                ReleaseTrackCreate(
                    version_id=sample_uuid,
                    track_number=1,
                ),
                ReleaseTrackCreate(
                    version_id=sample_uuid,
                    track_number=2,
                    disc_number=1,
                ),
            ],
        )

    def test_validate_defaults(self):
        release = ReleaseCreate(title="Test")

        assert release.release_date is None
        assert release.release_category is None
        assert release.catalog_number is None
        assert release.publisher_number is None
        assert release.label is None
        assert release.region is None
        assert release.release_stage is None
        assert release.cover_art_url is None
        assert release.total_discs is None
        assert release.total_tracks is None
        assert release.notes is None
        assert release.media_items is None
        assert release.tracks is None
        assert release.external_links is None

    def test_validate_missing_title_raises(self):
        with pytest.raises(ValidationError):
            ReleaseCreate()

    def test_validate_invalid_track_propagates(self):
        with pytest.raises(ValidationError) as exc_info:
            ReleaseCreate(
                title="Bad Track",
                tracks=[ReleaseTrackCreate(version_id="not-a-uuid", track_number=1)],
            )

        assert "Invalid UUID" in str(exc_info.value)
