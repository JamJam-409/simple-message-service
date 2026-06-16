from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    """Convert application exceptions into a consistent JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )
