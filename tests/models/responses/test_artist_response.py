from datetime import date

import pytest

from music_catalogue.models.responses.artists import (
    Artist,
    ArtistMembership,
    ArtistType,
)


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
        assert artist.members is None

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
