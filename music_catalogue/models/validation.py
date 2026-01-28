from datetime import date, datetime
from typing import Optional
from uuid import UUID


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
        raise ValueError(f"Invalid UUID {uuid}: {str(e)}") from None


def validate_date(date_str: str) -> date:
    """
    Check if a date has a valid format

    Args:
        date_str (str, optional): The date to check in ISO 8601 format (YYYY-MM-DD)

    Returns:
        date: The date object the string represents

    Raises:
        ValidationError: If the date is invalid
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise ValueError(f"Invalid date format {date_str}: {str(e)}") from None


def validate_year(year: int) -> None:
    """
    Check if a year is valid

    Args:
        year (str, optional): The year to check

    Raises:
        ValidationError: If the year is invalid
    """
    try:
        date(year=year, month=1, day=1)
    except ValueError as e:
        raise ValueError(f"Invalid year {year}: {str(e)}") from None


def validate_start_and_end_dates(start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
    """
    Check if a start and end date combination is valid by checking date formats and
    whether the start date is before the end date.

    Args:
        start_date (str, optional): The start date to check in ISO 8601 format (YYYY-MM-DD)
        end_date (str, optional): The end date to check in ISO 8601 format (YYYY-MM-DD)

    Raises:
        ValidationError: If either of the date strings or their combination is invalid
    """
    try:
        now = datetime.now().date()
        if start_date:
            # Check date is valid and in ISO 8601 format
            start_date = validate_date(start_date)
            # Check date is not in the future
            if start_date > now:
                raise ValueError("Start date can't be in the future")
        if end_date:
            end_date = validate_date(end_date)
            if end_date > now:
                raise ValueError("End date can't be in the future")

        if start_date and end_date:
            # Check end is before start
            if start_date > end_date:
                raise ValueError("Start date should be before or equal to end date.")

    except ValueError as e:
        raise ValueError(f"Invalid dates: {str(e)}") from None
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
            validate_year(start_year)
            # Check year is not in the future
            if start_year > now.year:
                raise ValueError("Start year can't be in the future")
        if end_year:
            validate_year(end_year)
            if end_year > now.year:
                raise ValueError("End year can't be in the future")

        if start_year and end_year:
            # Check start is before end
            if start_year > end_year:
                raise ValueError("Start year should be before or equal to end year.")

    except ValueError as e:
        raise ValueError(f"Invalid years: {str(e)}") from None
    except Exception as e:
        raise e
