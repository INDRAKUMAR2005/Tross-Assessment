# app/linkedin/auth.py
from app.config import Config
from app.exceptions import AuthRequiredException

class LinkedInAuth:
    @classmethod
    def get_cookies(cls) -> dict:
        """
        Retrieves authentication cookies configured in the environment.
        Raises AuthRequiredException if missing.
        """
        if not Config.LI_AT or not Config.JSESSIONID:
            raise AuthRequiredException(
                "LinkedIn authentication keys (LINKEDIN_LI_AT & LINKEDIN_JSESSIONID) "
                "are not set in the environment variables."
            )
            
        return {
            "li_at": Config.LI_AT,
            "JSESSIONID": Config.JSESSIONID
        }

    @classmethod
    def get_csrf_token(cls) -> str:
        """
        Extracts the csrf token from JSESSIONID.
        """
        jsessionid = Config.JSESSIONID or ""
        # Remove surrounding quotes if they exist
        return jsessionid.replace('"', '').strip()
