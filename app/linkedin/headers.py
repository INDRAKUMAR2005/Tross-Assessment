# app/linkedin/headers.py
from app.linkedin.auth import LinkedInAuth

class LinkedInHeaders:
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    @classmethod
    def get_default_headers(cls) -> dict:
        csrf_token = LinkedInAuth.get_csrf_token()
        return {
            "User-Agent": cls.DEFAULT_USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Csrf-Token": csrf_token,
            "X-RestLi-Protocol-Version": "2.0.0",
        }
