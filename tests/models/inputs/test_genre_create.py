import pytest
from pydantic import ValidationError

from music_catalogue.models.inputs.genre_create import GenreCreate


class TestGenreCreate:
    """Test the GenreCreate input model."""

    def test_valid_genre_with_all_fields(self):
        genre = GenreCreate(name="Jazz", description="A genre of music")
        assert genre.name == "Jazz"
        assert genre.description == "A genre of music"

    def test_valid_genre_name_only(self):
        genre = GenreCreate(name="Rock")
        assert genre.name == "Rock"
        assert genre.description is None

    def test_missing_name_raises_validation_error(self):
        with pytest.raises(ValidationError):
            GenreCreate()
