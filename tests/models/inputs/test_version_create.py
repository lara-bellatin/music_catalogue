import uuid
from datetime import date

import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.assets_create import ExternalLinkCreate
from music_catalogue.models.inputs.credit_create import CreditCreate
from music_catalogue.models.inputs.version_create import VersionCreate
from music_catalogue.models.types import CompletenessLevel, VersionType


class TestVersionCreate:
    """Tests for VersionCreate model."""

    def test_validate_minimal_success(self):
        VersionCreate(
            title="A Version",
            work_id=str(uuid.uuid4()),
            primary_artist_id=str(uuid.uuid4()),
        )

    def test_validate_full_success(self):
        VersionCreate(
            title="A Version",
            work_id=str(uuid.uuid4()),
            primary_artist_id=str(uuid.uuid4()),
            version_type=VersionType.LIVE,
            based_on_version_id=str(uuid.uuid4()),
            release_date=date(2020, 1, 1),
            release_year=2020,
            duration_seconds=600,
            bpm=120,
            key_signature="C minor",
            lyrics_reference="https://example.com/lyrics",
            completeness_level=CompletenessLevel.COMPLETE,
            notes="Recorded at venue",
            credits=[
                CreditCreate(
                    person_id=str(uuid.uuid4()),
                    version_id=str(uuid.uuid4()),
                    role="Performer",
                )
            ],
            external_links=[
                ExternalLinkCreate(
                    label="Spotify",
                    url="https://open.spotify.com/track/123",
                    added_by_id=str(uuid.uuid4()),
                )
            ],
        )

    def test_validate_invalid_work_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Work",
                work_id="not-a-uuid",
                primary_artist_id=str(uuid.uuid4()),
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_primary_artist_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Artist",
                work_id=str(uuid.uuid4()),
                primary_artist_id="not-a-uuid",
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_based_on_version_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Based On",
                work_id=str(uuid.uuid4()),
                primary_artist_id=str(uuid.uuid4()),
                based_on_version_id="not-a-uuid",
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_release_year_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Impossible Year",
                work_id=str(uuid.uuid4()),
                primary_artist_id=str(uuid.uuid4()),
                release_year=1234567890,
            )

        assert "Invalid year" in str(exc_info.value)

    def test_validate_invalid_credit_propagates(self):
        with pytest.raises(ValidationError) as exc_info:
            VersionCreate(
                title="Invalid Credit",
                work_id=str(uuid.uuid4()),
                primary_artist_id=str(uuid.uuid4()),
                credits=[CreditCreate(version_id=str(uuid.uuid4()), role="Composer")],
            )

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_defaults(self):
        version = VersionCreate(
            title="Defaults",
            work_id=str(uuid.uuid4()),
            primary_artist_id=str(uuid.uuid4()),
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
