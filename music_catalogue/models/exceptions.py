class ValidationError(Exception):
    """
    Exception raised when there's a validation error to do with the input.

    Attributes:
        message (str): Human-readable error message
    """

    pass


class APIError(Exception):
    """
    Exception raised when there's an error thrown by an API endpoint call.
    """

    pass
