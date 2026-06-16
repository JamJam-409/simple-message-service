class AppException(Exception):
    """Base exception for application errors returned by the API."""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


class MessageNotFoundException(AppException):
    """Raised when a message id does not exist."""

    def __init__(self):
        super().__init__(
            status_code=404,
            code="MESSAGE_NOT_FOUND",
            message="Message id does not exist",
        )


class InvalidIndexRangeException(AppException):
    """Raised when the message index range is invalid."""

    def __init__(self):
        super().__init__(
            status_code=400,
            code="INVALID_INDEX_RANGE",
            message="stop_index must be greater than or equal to start_index",
        )
