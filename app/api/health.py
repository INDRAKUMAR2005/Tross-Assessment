# app/api/health.py
from fastapi import APIRouter, status
from app.config import Config

router = APIRouter(tags=["System"])

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Checks the configuration health of the API (whether LinkedIn credentials are set).
    """
    cookie_auth = bool(Config.LI_AT and Config.JSESSIONID)
    
    if not cookie_auth:
        return {
            "status": "unconfigured",
            "message": "LinkedIn credentials are not configured in environment. API requests will fail.",
            "auth_method_configured": None
        }
        
    return {
        "status": "healthy",
        "message": "API configuration validated.",
        "auth_method_configured": "cookies"
    }
