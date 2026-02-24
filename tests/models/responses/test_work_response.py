import pytest

from music_catalogue.models.responses.genres import Genre
from music_catalogue.models.responses.references import CreditRef as WorkCredit
from music_catalogue.models.responses.works import Work


class TestGenre:
    """Test the Genre model"""

    def test_genre_from_dict_full_payload(self):
        payload = {
            "genre_id": "genre-1",
            "name": "Classical",
            "description": "Art music tradition",
        }

        genre = Genre.from_dict(payload)

        assert genre.id == "genre-1"
        assert genre.name == "Classical"
        assert genre.description == "Art music tradition"

    def test_genre_from_dict_missing_required_field(self):
        payload = {"name": "Classical"}
        with pytest.raises(KeyError):
            Genre.from_dict(payload)


class TestWork:
    """Test the Work model"""

    def test_work_from_dict_minimal_payload(self):
        payload = {"work_id": "work-1", "title": "Test Work"}

        work = Work.from_dict(payload)

        assert work.id == "work-1"
        assert work.title == "Test Work"
        assert work.language is None
        assert work.versions == []
        assert work.genres == []
        assert work.credits == []

    def test_work_from_dict_populates_nested_collections(self):
        payload = {
            "work_id": "work-2",
            "title": "Work 2",
            "language": "en",
            "work_genres": [
                {"genres": {"genre_id": "genre-2", "name": "Solo", "description": None}},
            ],
            "credits": [
                {
                    "credit_id": "credit-1",
                    "role": "Composer",
                    "is_primary": True,
                    "artist": {
                        "artist_id": "artist-7",
                        "artist_type": "solo",
                        "display_name": "Test Composer",
                    },
                    "person": {
                        "person_id": "person-3",
                        "legal_name": "Composer Name",
                    },
                }
            ],
        }

        work = Work.from_dict(payload)

        assert work.language == "en"
        assert len(work.genres) == 1
        assert work.genres[0].id == "genre-2"
        assert len(work.credits) == 1
        assert work.credits[0].role == "Composer"
        assert work.credits[0].is_primary is True
        assert work.credits[0].artist is not None
        assert work.credits[0].person is not None

    def test_work_from_dict_missing_required_field(self):
        payload = {"title": "No ID Work"}
        with pytest.raises(KeyError):
            Work.from_dict(payload)


class TestWorkCredit:
    """Test the WorkCredit model"""

    def test_credit_from_dict_with_related_entities(self):
        payload = {
            "credit_id": "credit-99",
            "artist": {
                "artist_id": "artist-42",
                "artist_type": "solo",
                "display_name": "Featured Artist",
            },
            "person": {
                "person_id": "person-9",
                "legal_name": "Featured Person",
            },
            "role": "Vocals",
            "is_primary": True,
            "credit_order": 1,
            "instruments": ["Voice"],
            "notes": "Lead performance",
        }

        credit = WorkCredit.from_dict(payload)

        assert credit.role == "Vocals"
        assert credit.is_primary is True
        assert credit.credit_order == 1
        assert credit.instruments == ["Voice"]
        assert credit.notes == "Lead performance"
        assert credit.artist is not None and credit.artist.name == "Featured Artist"
        assert credit.person is not None and credit.person.name == "Featured Person"

    def test_credit_from_dict_missing_required_field(self):
        payload = {"role": "Vocals"}
        with pytest.raises(KeyError):
            WorkCredit.from_dict(payload)
