# app/utils/url_validator.py
import re
from typing import Optional
from urllib.parse import unquote
from app.exceptions import InvalidProfileURLException

# Regex to match:
# - https://www.linkedin.com/in/username
# - https://linkedin.com/in/username/
# - linkedin.com/in/username
LINKEDIN_URL_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_\-\u00C0-\u00FF%]+)",
    re.IGNORECASE
)

class LinkedInProfileIdentifier:
    @staticmethod
    def extract_public_id(url: str) -> str:
        """
        Extracts the profile identifier (vanity name) from a LinkedIn URL.
        Raises InvalidProfileURLException if malformed.
        """
        if not url:
            raise InvalidProfileURLException("Profile URL cannot be empty.")
            
        match = LINKEDIN_URL_REGEX.search(url)
        if not match:
            raise InvalidProfileURLException(
                f"Invalid LinkedIn profile URL: '{url}'. "
                "Must match pattern: linkedin.com/in/<username>"
            )
            
        return unquote(match.group(1))
