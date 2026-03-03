from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class BaseHTTPError(HTTPException):
    def __init__(self, status_code: int, detail: str = "An error occurred"):
        super().__init__(
            status_code=status_code,
            detail={"error_type": type(self).__name__, "msg": detail},
        )


class AlreadyExistsError(Exception):
    pass


class AlreadyRegisteredHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UserNotFoundHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ServerHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class InvalidOrExpiredTokenHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class PermissionDeniedHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidPasswordHTTPError(BaseHTTPError):
    def __init__(self, detail: str = "Invalid password"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class InvalidOrExpiredTokenError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


async def base_error_handler(request: Request, exc: BaseHTTPError):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=jsonable_encoder({"code": 500, "err": str(exc)}))
