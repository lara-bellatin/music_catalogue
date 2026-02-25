import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.credit_create import CreditCreate


class TestCreditCreate:
    """Tests for CreditCreate model."""

    def test_validate_with_person_id_success(self, sample_uuid):
        CreditCreate(person_id=sample_uuid, work_id=sample_uuid, role="Composer")

    def test_validate_with_artist_id_success(self, sample_uuid):
        CreditCreate(artist_id=sample_uuid, work_id=sample_uuid, role="Composer")

    def test_validate_with_version_id_success(self, sample_uuid):
        CreditCreate(person_id=sample_uuid, version_id=sample_uuid, role="Performer")

    def test_validate_missing_person_artist_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            CreditCreate(work_id=sample_uuid, role="Composer")

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_both_person_artist_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            CreditCreate(
                person_id=sample_uuid,
                artist_id=sample_uuid,
                work_id=sample_uuid,
                role="Composer",
            )

        assert "Either person or artist ID" in str(exc_info.value)

    def test_validate_missing_work_version_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            CreditCreate(person_id=sample_uuid, role="Composer")

        assert "Either work or version ID" in str(exc_info.value)

    def test_validate_both_work_version_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            CreditCreate(
                person_id=sample_uuid,
                work_id=sample_uuid,
                version_id=sample_uuid,
                role="Composer",
            )

        assert "Either work or version ID" in str(exc_info.value)
