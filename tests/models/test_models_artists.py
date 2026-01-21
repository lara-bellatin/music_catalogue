import uuid
from datetime import date

import pytest

from music_catalogue.models.artists import (
    Artist,
    ArtistCreate,
    ArtistMembership,
    ArtistMembershipCreate,
    ArtistType,
)
from music_catalogue.models.exceptions import ValidationError


class TestArtist:
    """Test the Artist and ArtistMembership models"""

    def test_group_artist_from_dict(self):
        payload = {
            "artist_id": "artist-1",
            "artist_type": "solo",
            "display_name": "Test Band",
            "sort_name": "Test Band",
            "alternative_names": ["Test"],
            "start_year": 2008,
            "end_year": None,
            "artist_memberships": [
                {
                    "membership_id": "membership-1",
                    "person": {
                        "person_id": "person-1",
                        "legal_name": "John Smith",
                    },
                    "start_year": 2010,
                    "role": "Guitar",
                }
            ],
        }

        artist = Artist.from_dict(payload)

        assert artist.id == "artist-1"
        assert artist.artist_type is ArtistType.SOLO
        assert artist.display_name == "Test Band"
        assert artist.sort_name == "Test Band"
        assert artist.alternative_names == ["Test"]
        assert artist.start_year == 2008
        assert artist.end_year is None
        assert len(artist.members) == 1
        membership = artist.members[0]
        assert membership.id == "membership-1"
        assert membership.person is not None and membership.person.legal_name == "John Smith"
        assert membership.role == "Guitar"

    def test_solo_artist_from_dict(self):
        payload = {
            "artist_id": "artist-2",
            "artist_type": "solo",
            "display_name": "John Smith",
            "person": {
                "person_id": "person-3",
                "legal_name": "John Smith",
                "birth_date": "2000-01-01",
            },
        }

        artist = Artist.from_dict(payload)

        assert artist.artist_type is ArtistType.SOLO
        assert artist.person.id == "person-3"
        assert artist.person.legal_name == "John Smith"
        assert artist.person.birth_date == date(2000, 1, 1)
        assert artist.members == []

    def test_missing_required_fields(self):
        payload = {
            "artist_id": None,
            "artist_type": "solo",
            "display_name": "John Smith",
            "person": {
                "person_id": "person-3",
                "legal_name": "John Smith",
                "birth_date": "2000-01-01",
            },
        }

        with pytest.raises(ValueError):
            Artist.from_dict(payload)

    def test_artist_membership_from_dict_minimal_payload(self):
        payload = {
            "membership_id": "membership-2",
            "artist": None,
            "person": {
                "person_id": "person-5",
                "legal_name": "John Smith",
            },
            "start_year": 2015,
            "end_year": 2018,
            "role": "Drums",
            "notes": "Founding member",
        }

        membership = ArtistMembership.from_dict(payload)

        assert membership.id == "membership-2"
        assert membership.artist is None
        assert membership.person is not None and membership.person.legal_name == "John Smith"
        assert membership.start_year == 2015
        assert membership.end_year == 2018
        assert membership.role == "Drums"
        assert membership.notes == "Founding member"


class TestArtistCreate:
    """Tests for ArtistCreate model."""

    def test_validate_solo_artist_success(self):
        artist = ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="Solo Artist",
            person_id=str(uuid.uuid4()),
            start_year=1990,
            end_year=2000,
        )

        artist.validate()

    def test_validate_solo_missing_person_raises(self):
        artist = ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="No Person",
        )

        with pytest.raises(ValidationError) as exc_info:
            artist.validate()

        assert "Missing person ID" in str(exc_info.value)

    def test_validate_solo_with_members_raises(self):
        artist = ArtistCreate(
            artist_type=ArtistType.SOLO,
            display_name="Solo With Members",
            person_id=str(uuid.uuid4()),
            members=[ArtistMembershipCreate(person_id=str(uuid.uuid4()))],
        )

        with pytest.raises(ValidationError) as exc_info:
            artist.validate()

        assert "There cannot be members" in str(exc_info.value)

    def test_validate_group_artist_success(self):
        artist = ArtistCreate(
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

        artist.validate()

    def test_validate_group_missing_members_raises(self):
        artist = ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="Memberless Group",
        )

        with pytest.raises(ValidationError) as exc_info:
            artist.validate()

        assert "Missing members" in str(exc_info.value)

    def test_validate_group_with_person_id_raises(self):
        artist = ArtistCreate(
            artist_type=ArtistType.GROUP,
            display_name="Group With Person",
            person_id=str(uuid.uuid4()),
            members=[ArtistMembershipCreate(person_id=str(uuid.uuid4()))],
        )

        with pytest.raises(ValidationError) as exc_info:
            artist.validate()

        assert "Invalid assignment of person" in str(exc_info.value)


class TestArtistMembershipCreateValidation:
    """Tests for ArtistMembershipCreate.validate."""

    def test_validate_membership_success(self):
        membership = ArtistMembershipCreate(
            person_id=str(uuid.uuid4()),
            start_year=1990,
            end_year=1995,
        )

        membership.validate()

    def test_validate_membership_invalid_uuid_raises(self):
        membership = ArtistMembershipCreate(person_id="not-a-uuid")

        with pytest.raises(ValidationError) as exc_info:
            membership.validate()

        assert "Invalid member configuration" in str(exc_info.value)

    def test_validate_membership_invalid_year_range_raises(self):
        membership = ArtistMembershipCreate(
            person_id=str(uuid.uuid4()),
            start_year=2000,
            end_year=1990,
        )

        with pytest.raises(ValidationError) as exc_info:
            membership.validate()

        assert "Invalid member configuration" in str(exc_info.value)
