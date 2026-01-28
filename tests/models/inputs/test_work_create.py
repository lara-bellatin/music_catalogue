import uuid

import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.work_create import (
    VersionType,
    WorkCreate,
    WorkCreditCreate,
    WorkVersionCreate,
)


class TestWorkCreditCreate:
    """Tests for WorkCreditCreate model."""

    def test_validate_with_person_id_success(self):
        WorkCreditCreate(person_id=str(uuid.uuid4()), role="Composer")

    def test_validate_with_artist_id_success(self):
        WorkCreditCreate(artist_id=str(uuid.uuid4()), role="Composer")

    def test_validate_missing_identifiers_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreditCreate(role="Composer")

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_both_identifiers_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreditCreate(
                person_id=str(uuid.uuid4()),
                artist_id=str(uuid.uuid4()),
                role="Composer",
            )

        assert "Either person or artist ID" in str(exc_info.value)


class TestWorkVersionCreate:
    """Tests for WorkVersionCreate model."""

    def test_validate_success(self):
        WorkVersionCreate(
            title="A Work Version",
            primary_artist_id=str(uuid.uuid4()),
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

    def test_validate_invalid_release_year_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkVersionCreate(
                title="Impossible Year",
                primary_artist_id=str(uuid.uuid4()),
                release_year=1234567890,
            )

        assert "Invalid year" in str(exc_info.value)


class TestWorkCreate:
    """Tests for WorkCreate model."""

    def test_validate_success(self):
        WorkCreate(
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

    def test_validate_invalid_year_range_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreate(title="Invalid Years", origin_year_start=2000, origin_year_end=1990)

        assert "Start year" in str(exc_info.value)

    def test_validate_invalid_credit_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            WorkCreate(title="Missing Credit IDs", credits=[WorkCreditCreate(role="Composer")])

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
