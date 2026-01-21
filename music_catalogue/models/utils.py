from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from music_catalogue.models.exceptions import ValidationError

if TYPE_CHECKING:
    from music_catalogue.models.artists import Artist
    from music_catalogue.models.persons import Person
    from music_catalogue.models.works import Credit, Genre, Release, ReleaseMediaItem, Version, Work


class EntityType(str, Enum):
    PERSON = "person"
    ARTIST = "artist"
    WORK = "work"
    VERSION = "version"
    RELEASE = "release"
    MEDIA_ITEM = "media_item"
    CREDIT = "credit"
    GENRE = "genre"


type AnyEntityType = Union[Person, Artist, Work, Version, Release, ReleaseMediaItem, Credit, Genre]


class UnifiedSearchResult(BaseModel):
    entity_type: EntityType
    entity_id: str
    display_text: str
    rank: float

    @classmethod
    def from_dict(cls, data: Dict) -> "UnifiedSearchResult":
        return cls(
            entity_type=EntityType(data["entity_type"]),
            entity_id=data["entity_id"],
            display_text=data["display_text"],
            rank=data["rank"],
        )


def _parse(model_cls: BaseModel, data: Dict) -> AnyEntityType:
    if not data:
        return None
    return model_cls.from_dict(data)


def _parse_list(model_cls: BaseModel, data: Dict) -> List[AnyEntityType]:
    if not data:
        return []
    return [_parse(model_cls, item) for item in data if _parse(model_cls, item) is not None]


def validate_uuid(uuid: str) -> None:
    """
    Check if a string is a valid UUID

    Args:
        uuid (str): The UUID to test

    Raises:
        ValidationError: If the UUID is invalid
    """
    try:
        UUID(uuid)
    except ValueError as e:
        raise ValidationError(f"Invalid UUID format: {str(e)}") from None


def validate_start_and_end_dates(start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
    """
    Check if a start and end date combination is valid by checking date formats and
    whether the start date is before the end date.

    Args:
        start_date (str, optional): The start date to check in ISO 8601 format (YYYY-MM-DD)
        end_date (str, optional): The end date to check in ISO 8601 format (YYYY-MM-DD)

    Raises:
        ValidationError: if either of the date strings or their combination is invalid
    """
    try:
        now = datetime.now().date()
        if start_date:
            # Check date is valid and in ISO 8601 format
            start_date = date.fromisoformat(start_date)
            # Check date is not in the future
            if start_date > now:
                raise ValidationError("Start date can't be in the future")
        if end_date:
            end_date = date.fromisoformat(end_date)
            if end_date > now:
                raise ValidationError("End date can't be in the future")

        if start_date and end_date:
            # Check end is before start
            if start_date > end_date:
                raise ValidationError("Start date should be before or equal to end date.")

    except ValueError as e:
        raise ValidationError(f"Invalid dates: {str(e)}") from None
    except Exception as e:
        raise e


def validate_start_and_end_years(start_year: Optional[int] = None, end_year: Optional[int] = None) -> None:
    """
    Check if a start and end year combination is valid

    Args:
        start_year (int, optional): The start year to check
        end_year (int, optional): The end year to check

    Raises:
        ValidationError: If either of the years or their combination is invalid
    """
    try:
        now = datetime.now().date()
        if start_year:
            # Check year is valid
            date(year=start_year, month=1, day=1)
            # Check year is not in the future
            if start_year > now.year:
                raise ValidationError("Start year can't be in the future")
        if end_year:
            date(year=end_year, month=1, day=1)
            if end_year > now.year:
                raise ValidationError("End year can't be in the future")

        if start_year and end_year:
            # Check start is before end
            if start_year > end_year:
                raise ValidationError("Start year should be before or equal to end year.")

    except ValueError as e:
        raise ValidationError(f"Invalid years: {str(e)}") from None
    except Exception as e:
        raise e
