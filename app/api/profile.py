# app/api/profile.py
import logging
from fastapi import APIRouter, status, HTTPException
from app.models.request import ProfileRequest
from app.models.response import ProfileResponse
from app.utils.url_validator import LinkedInProfileIdentifier
from app.linkedin.client import LinkedInClient
from app.linkedin.parser import LinkedInParser

logger = logging.getLogger(__name__)
router = APIRouter(tags=["LinkedIn Scraper"])

# Define handler function
async def fetch_and_parse_profile(payload: ProfileRequest) -> ProfileResponse:
    # 1. Parse and validate URL to extract username
    public_id = LinkedInProfileIdentifier.extract_public_id(payload.profile_url)
    
    # 2. Query LinkedIn endpoints directly using HTTPX
    client = LinkedInClient()
    logger.info(f"Scraping profile for: {public_id} via direct HTTP request...")
    
    # Fetch core profile
    raw_profile = await client.get_raw_profile_view(public_id)
    
    # Fetch contact info (optional, won't block if failed)
    raw_contact = await client.get_raw_contact_info(public_id)
    
    # 3. Parse and normalize response
    normalized = LinkedInParser.normalize_profile(public_id, raw_profile, raw_contact)
    return normalized

# Mount both routes for full backward compatibility & master prompt compliance
@router.post(
    "/api/v1/linkedin/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape LinkedIn Profile Data (New Route)"
)
async def get_linkedin_profile_new(payload: ProfileRequest):
    return await fetch_and_parse_profile(payload)

@router.post(
    "/api/v1/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape LinkedIn Profile Data (Old Route)",
    include_in_schema=False
)
async def get_linkedin_profile_old(payload: ProfileRequest):
    return await fetch_and_parse_profile(payload)
