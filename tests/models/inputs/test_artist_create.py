import uuid

import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.artist_create import (
    ArtistCreate,
    ArtistMembershipCreate,
    ArtistType,
)


class TestArtistCreate:
    """Tests for ArtistCreate model."""

    def test_validate_solo_artist_success(self):
        ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="Solo Artist",
            person_id=str(uuid.uuid4()),
            start_year=1990,
            end_year=2000,
        )

    def test_validate_solo_missing_person_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ArtistCreate(
                artist_type=ArtistType.SOLO,
                display_name="No Person",
            )

        assert "Missing person ID" in str(exc_info.value)

    def test_validate_solo_with_members_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ArtistCreate(
                artist_type=ArtistType.SOLO,
                display_name="Solo With Members",
                person_id=str(uuid.uuid4()),
                members=[ArtistMembershipCreate(person_id=str(uuid.uuid4()))],
            )

        assert "There cannot be members" in str(exc_info.value)

    def test_validate_group_artist_success(self):
        ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="The Group",
            members=[
                ArtistMembershipCreate(
                    person_id=str(uuid.uuid4()),
                    start_year=1995,
                    end_year=2005,
                )
            ],
        )

    def test_validate_group_missing_members_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ArtistCreate(
                artist_type=ArtistType.GROUP,
                display_name="Memberless Group",
            )

        assert "Missing members" in str(exc_info.value)

    def test_validate_group_with_person_id_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ArtistCreate(
                artist_type=ArtistType.GROUP,
                display_name="Group With Person",
                person_id=str(uuid.uuid4()),
                members=[ArtistMembershipCreate(person_id=str(uuid.uuid4()))],
            )

        assert "Invalid assignment of person" in str(exc_info.value)


class TestArtistMembershipCreateValidation:
    """Tests for ArtistMembershipCreate.validate."""

    def test_validate_membership_success(self):
        ArtistMembershipCreate(
            person_id=str(uuid.uuid4()),
            start_year=1990,
            end_year=1995,
        )

    def test_validate_membership_invalid_uuid_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ArtistMembershipCreate(person_id="not-a-uuid")

        assert "Invalid member configuration" in str(exc_info.value)

    def test_validate_membership_invalid_year_range_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ArtistMembershipCreate(
                person_id=str(uuid.uuid4()),
                start_year=2000,
                end_year=1990,
            )

        assert "Invalid member configuration" in str(exc_info.value)
