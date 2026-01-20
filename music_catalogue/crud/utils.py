from datetime import date, datetime
from uuid import UUID

from music_catalogue.models.exceptions import ValidationError


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


def validate_start_and_end_dates(start_date: str, end_date: str) -> None:
    """
    Check if a start and end date combination is valid by checking date formats and
    whether the start date is before the end date.

    Args:
        start_date (str): The start date to check in ISO 8601 format (YYYY-MM-DD)
        end_date (str): The end date to check in ISO 8601 format (YYYY-MM-DD)

    Raises:
        ValidationError: if either of the date strings or their combination is invalid
    """
    try:
        now = datetime.now().date()
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        if start_date > now or end_date > now:
            raise ValidationError("Start and end dates can't be in the future.")

        if start_date > end_date:
            raise ValidationError("Start date should be before or equal to end date.")

    except ValueError as e:
        raise ValidationError(f"Invalid date format: {str(e)}") from None
    except Exception as e:
        raise e


def validate_start_and_end_years(start_year: int, end_year: int) -> None:
    """
    Check if a start and end year combination is valid

    Args:
        start_year (int): The start year to check
        end_year (int): The end year to check

    Raises:
        ValidationError: If either of the years or their combination is invalid
    """
    try:
        now = datetime.now().date()
        start_date = date(year=start_year, month=1, day=1)
        end_date = date(year=end_year, month=1, day=1)

        if start_date > now or end_date > now:
            raise ValidationError("Start and end years can't be in the future.")

        if start_date > end_date:
            raise ValidationError("Start year should be before or equal to end year.")

    except ValueError as e:
        raise ValidationError(f"Invalid year format: {str(e)}") from None
    except Exception as e:
        raise e
