# app/config.py
import os
from dotenv import load_dotenv

# Load local .env if it exists
load_dotenv()

class Config:
    # Server config
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # API key protection
    API_KEY = os.getenv("API_KEY", "")
    API_KEY_ENABLED = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    
    # LinkedIn credentials
    LI_AT = os.getenv("LINKEDIN_LI_AT", "").strip().strip('"').strip("'")
    JSESSIONID = os.getenv("LINKEDIN_JSESSIONID", "").strip().strip('"').strip("'")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        if not cls.LI_AT or not cls.JSESSIONID:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "LINKEDIN_LI_AT or LINKEDIN_JSESSIONID is missing in environment. "
                "Calls requiring authorization will fail."
            )
