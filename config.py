import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load local .env file if it exists
load_dotenv()

class Config:
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # LinkedIn Authentication via cookies (Recommended)
    LI_AT = os.getenv("LINKEDIN_LI_AT")
    JSESSIONID = os.getenv("LINKEDIN_JSESSIONID")
    
    # LinkedIn Authentication via credentials (Fallback)
    USERNAME = os.getenv("LINKEDIN_USERNAME")
    PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    
    @classmethod
    def is_cookie_auth_available(cls) -> bool:
        return bool(cls.LI_AT and cls.JSESSIONID)

    @classmethod
    def is_password_auth_available(cls) -> bool:
        return bool(cls.USERNAME and cls.PASSWORD)

    @classmethod
    def validate_config(cls):
        if not cls.is_cookie_auth_available() and not cls.is_password_auth_available():
            logger.warning(
                "CRITICAL WARNING: LinkedIn credentials are not configured! "
                "Please configure LINKEDIN_LI_AT & LINKEDIN_JSESSIONID (Recommended) "
                "or LINKEDIN_USERNAME & LINKEDIN_PASSWORD in your .env file."
            )
        else:
            if cls.is_cookie_auth_available():
                logger.info("LinkedIn Cookie Authentication is configured.")
            else:
                logger.info("LinkedIn Username/Password Authentication is configured.")

# Run validation on import
Config.validate_config()
