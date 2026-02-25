import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.inputs.credit_create import WorkVersionCreditCreate
from music_catalogue.models.inputs.version_create import VersionCreate
from music_catalogue.models.types import CompletenessLevel, VersionType


class TestVersionCreate:
    """Tests for VersionCreate model."""

    def test_validate_minimal_success(self, sample_uuid):
        VersionCreate(
            title="A Version",
            work_id=sample_uuid,
            primary_artist_id=sample_uuid,
        )

    def test_validate_full_success(self, sample_uuid):
        VersionCreate(
            title="A Version",
            work_id=sample_uuid,
            primary_artist_id=sample_uuid,
            version_type=VersionType.LIVE,
            based_on_version_id=sample_uuid,
            release_date="2020-01-01",
            release_year=2020,
            duration_seconds=600,
            bpm=120,
            key_signature="C minor",
            lyrics_reference="https://example.com/lyrics",
            completeness_level=CompletenessLevel.COMPLETE,
            notes="Recorded at venue",
            credits=[
                WorkVersionCreditCreate(
                    person_id=sample_uuid,
                    version_id=sample_uuid,
                    role="Performer",
                )
            ],
            external_links=[
                ExternalLinkCreate(
                    label="Spotify",
                    url="https://open.spotify.com/track/123",
                    added_by_id=sample_uuid,
                )
            ],
        )

    def test_validate_invalid_work_id_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Work",
                work_id="not-a-uuid",
                primary_artist_id=sample_uuid,
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_primary_artist_id_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Artist",
                work_id=sample_uuid,
                primary_artist_id="not-a-uuid",
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_based_on_version_id_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Based On",
                work_id=sample_uuid,
                primary_artist_id=sample_uuid,
                based_on_version_id="not-a-uuid",
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_release_year_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Impossible Year",
                work_id=sample_uuid,
                primary_artist_id=sample_uuid,
                release_year=1234567890,
            )

        assert "Invalid year" in str(exc_info.value)

    def test_validate_invalid_credit_propagates(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Credit",
                work_id=sample_uuid,
                primary_artist_id=sample_uuid,
                credits=[WorkVersionCreditCreate(version_id=sample_uuid, role="Composer")],
            )

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_defaults(self, sample_uuid):
        version = VersionCreate(
            title="Defaults",
            work_id=sample_uuid,
            primary_artist_id=sample_uuid,
        )

        assert version.version_type is VersionType.ORIGINAL
        assert version.completeness_level is CompletenessLevel.COMPLETE
        assert version.based_on_version_id is None
        assert version.release_date is None
        assert version.release_year is None
        assert version.duration_seconds is None
        assert version.bpm is None
        assert version.key_signature is None
        assert version.credits is None
        assert version.external_links is None
