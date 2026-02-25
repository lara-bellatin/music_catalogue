import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.performance_create import (
    PerformanceArtistCreate,
    PerformanceCreate,
    PerformanceWorkCreate,
)


class TestPerformanceArtistCreate:
    """Tests for PerformanceArtistCreate model."""

    def test_validate_with_artist_id_success(self, sample_uuid):
        PerformanceArtistCreate(
            artist_id=sample_uuid,
            role="headliner",
            billing_order=1,
        )

    def test_validate_with_person_id_success(self, sample_uuid):
        PerformanceArtistCreate(
            person_id=sample_uuid,
            role="conductor",
        )

    def test_validate_neither_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceArtistCreate(role="headliner")

        assert "Exactly one of artist_id or person_id" in str(exc_info.value)

    def test_validate_both_ids_raises(self, sample_uuid):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceArtistCreate(
                artist_id=sample_uuid,
                person_id=sample_uuid,
                role="headliner",
            )

        assert "Exactly one of artist_id or person_id" in str(exc_info.value)

    def test_validate_invalid_artist_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceArtistCreate(artist_id="not-a-uuid", role="headliner")

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_person_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceArtistCreate(person_id="not-a-uuid", role="soloist")

        assert "Invalid UUID" in str(exc_info.value)


class TestPerformanceWorkCreate:
    """Tests for PerformanceWorkCreate model."""

    def test_validate_with_work_id_success(self, sample_uuid):
        PerformanceWorkCreate(
            work_id=sample_uuid,
            set_order=1,
            set_name="Main Set",
        )

    def test_validate_with_version_id_success(self, sample_uuid):
        PerformanceWorkCreate(
            version_id=sample_uuid,
            set_order=2,
        )

    def test_validate_with_both_ids_success(self, sample_uuid):
        PerformanceWorkCreate(
            work_id=sample_uuid,
            version_id=sample_uuid,
            set_order=1,
        )

    def test_validate_neither_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceWorkCreate(set_order=1, set_name="Encore")

        assert "At least one of work_id or version_id" in str(exc_info.value)

    def test_validate_invalid_work_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceWorkCreate(work_id="not-a-uuid", set_order=1)

        assert "Invalid UUID" in str(exc_info.value)

    def test_validate_invalid_version_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceWorkCreate(version_id="not-a-uuid", set_order=1)

        assert "Invalid UUID" in str(exc_info.value)


class TestPerformanceCreate:
    """Tests for PerformanceCreate model."""

    def test_validate_minimal_success(self):
        PerformanceCreate(name="Wembley Stadium 2024")

    def test_validate_full_success(self, sample_uuid):
        PerformanceCreate(
            name="Wembley Stadium 2024",
            performance_date="2024-06-15",
            venue="Wembley Stadium",
            city="London",
            country="UK",
            notes="Sold out show",
            artists=[
                PerformanceArtistCreate(
                    artist_id=sample_uuid,
                    role="headliner",
                    billing_order=1,
                ),
                PerformanceArtistCreate(
                    person_id=sample_uuid,
                    role="conductor",
                    billing_order=2,
                ),
            ],
            works=[
                PerformanceWorkCreate(
                    work_id=sample_uuid,
                    set_order=1,
                    set_name="Main Set",
                ),
                PerformanceWorkCreate(
                    version_id=sample_uuid,
                    set_order=2,
                    set_name="Encore",
                ),
            ],
        )

    def test_validate_defaults(self):
        perf = PerformanceCreate(name="Test")

        assert perf.performance_date is None
        assert perf.venue is None
        assert perf.city is None
        assert perf.country is None
        assert perf.notes is None
        assert perf.artists is None
        assert perf.works is None
        assert perf.external_links is None

    def test_validate_invalid_artist_propagates(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceCreate(
                name="Bad Artist",
                artists=[PerformanceArtistCreate(role="headliner")],
            )

        assert "Exactly one of artist_id or person_id" in str(exc_info.value)

    def test_validate_invalid_work_propagates(self):
        with pytest.raises(ValidationError) as exc_info:
            PerformanceCreate(
                name="Bad Work",
                works=[PerformanceWorkCreate(set_order=1)],
            )

        assert "At least one of work_id or version_id" in str(exc_info.value)
