import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.credit_create import WorkVersionCreditCreate
from music_catalogue.models.inputs.work_create import (
    WorkCreate,
    WorkVersionCreate,
)
from music_catalogue.models.types import VersionType


class TestWorkVersionCreate:
    """Tests for WorkVersionCreate model."""

    def test_validate_success(self, sample_uuid):
        WorkVersionCreate(
            title="A Work Version",
            primary_artist_id=sample_uuid,
            version_type=VersionType.LIVE,
            release_year=1990,
            duration_seconds=480,
        )

    def test_validate_invalid_primary_artist_uuid_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkVersionCreate(
                title="Invalid Artist",
                primary_artist_id="not-a-uuid",
            )

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_release_year_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            WorkVersionCreate(
                title="Impossible Year",
                primary_artist_id=sample_uuid,
                release_year=1234567890,
            )

        assert "Invalid year" in str(exc_info.value)


class TestWorkCreate:
    """Tests for WorkCreate model."""

    def test_validate_success(self, sample_uuid):
        work_id = sample_uuid
        WorkCreate(
            title="A Work",
            origin_year_start=1900,
            origin_year_end=1950,
            genre_ids=[sample_uuid],
            credits=[WorkVersionCreditCreate(person_id=sample_uuid, work_id=work_id, role="Composer")],
            versions=[
                WorkVersionCreate(
                    title="A Version",
                    primary_artist_id=sample_uuid,
                    version_type=VersionType.ORIGINAL,
                )
            ],
        )

    def test_validate_invalid_year_range_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreate(title="Invalid Years", origin_year_start=2000, origin_year_end=1990)

        assert "Start year" in str(exc_info.value)

    def test_validate_invalid_credit_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreate(
                title="Missing Credit IDs", credits=[WorkVersionCreditCreate(work_id=sample_uuid, role="Composer")]
            )

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_invalid_genre_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreate(title="Invalid Genre ID", genre_ids=["not-a-uuid"])

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_version_propagates(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreate(
                title="Invalid Version",
                versions=[WorkVersionCreate(title="Broken", primary_artist_id="not-a-uuid")],
            )

        assert "Invalid UUID" in str(exc_info.value)
