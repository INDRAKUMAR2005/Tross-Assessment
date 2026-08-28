# app/exceptions.py
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "code": code,
                    "message": message
                }
            }
        )

class InvalidProfileURLException(BaseAPIException):
    def __init__(self, message: str = "Invalid LinkedIn profile URL."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_LINKEDIN_URL",
            message=message
        )

class ProfileNotFoundException(BaseAPIException):
    def __init__(self, message: str = "Unable to retrieve the requested LinkedIn profile."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="PROFILE_NOT_FOUND",
            message=message
        )

class AuthRequiredException(BaseAPIException):
    def __init__(self, message: str = "LinkedIn authentication is required."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="LINKEDIN_AUTH_REQUIRED",
            message=message
        )

class AuthFailedException(BaseAPIException):
    def __init__(self, message: str = "LinkedIn authentication failed."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="LINKEDIN_AUTH_FAILED",
            message=message
        )

class RequestFailedException(BaseAPIException):
    def __init__(self, message: str = "Unable to retrieve the requested LinkedIn profile."):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="LINKEDIN_REQUEST_FAILED",
            message=message
        )

class RateLimitedException(BaseAPIException):
    def __init__(self, message: str = "LinkedIn requests are rate limited."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="LINKEDIN_RATE_LIMITED",
            message=message
        )

class AccessDeniedException(BaseAPIException):
    def __init__(self, message: str = "Access denied by LinkedIn."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="LINKEDIN_ACCESS_DENIED",
            message=message
        )

class ResponseStructureChangedException(BaseAPIException):
    def __init__(self, message: str = "LinkedIn response structure has changed."):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="LINKEDIN_RESPONSE_CHANGED",
            message=message
        )
