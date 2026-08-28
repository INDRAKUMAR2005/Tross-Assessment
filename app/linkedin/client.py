# app/linkedin/client.py
import httpx
import logging
import time
from typing import Dict, Any, Optional
from app.linkedin.auth import LinkedInAuth
from app.linkedin.headers import LinkedInHeaders
from app.linkedin.endpoints import LinkedInEndpoints
from app.exceptions import (
    AuthFailedException,
    AccessDeniedException,
    ProfileNotFoundException,
    RateLimitedException,
    RequestFailedException
)

logger = logging.getLogger(__name__)

class LinkedInClient:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

    async def get_raw_profile_view(self, public_id: str) -> Dict[str, Any]:
        """
        Queries LinkedIn's profileView Voyager endpoint directly using HTTPX.
        """
        url = LinkedInEndpoints.profile_view(public_id)
        headers = LinkedInHeaders.get_default_headers()
        cookies = LinkedInAuth.get_cookies()

        start_time = time.time()
        logger.info(f"Initiating direct HTTP GET request to profile view endpoint: {url}")
        
        async with httpx.AsyncClient(limits=self.limits, timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, cookies=cookies)
                duration = time.time() - start_time
                logger.info(f"Received response from LinkedIn with status {response.status_code} in {duration:.2f}s")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthFailedException("LinkedIn session authentication expired or invalid.")
                elif response.status_code == 403:
                    raise AccessDeniedException("Access denied by LinkedIn. The profile might be private or restricted.")
                elif response.status_code == 404:
                    raise ProfileNotFoundException(f"LinkedIn profile with identifier '{public_id}' not found.")
                elif response.status_code == 429:
                    raise RateLimitedException("LinkedIn rate limits reached. Try rotating cookies or scaling down requests.")
                else:
                    raise RequestFailedException(
                        f"LinkedIn request failed with status: {response.status_code}"
                    )
            except httpx.HTTPError as exc:
                logger.error(f"HTTP communication error: {exc}")
                raise RequestFailedException(f"Network error communicating with LinkedIn: {exc}")

    async def get_raw_contact_info(self, public_id: str) -> Optional[Dict[str, Any]]:
        """
        Queries LinkedIn's profileContactInfo Voyager endpoint directly using HTTPX.
        """
        url = LinkedInEndpoints.contact_info(public_id)
        headers = LinkedInHeaders.get_default_headers()
        cookies = LinkedInAuth.get_cookies()

        logger.info(f"Initiating direct HTTP GET request to contact info endpoint: {url}")
        
        async with httpx.AsyncClient(limits=self.limits, timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, cookies=cookies)
                if response.status_code == 200:
                    return response.json()
                else:
                    # Contact info failure should not block primary profile retrieval
                    logger.warning(
                        f"Contact info request returned status: {response.status_code}. "
                        "Often requires a 1st-degree connection or is restricted by settings."
                    )
                    return None
            except Exception as exc:
                logger.warning(f"Failed to fetch contact details due to request exception: {exc}")
                return None

