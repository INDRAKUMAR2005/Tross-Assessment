import re
import requests
import logging
from typing import Dict, Any, Optional
from open_linkedin_api import Linkedin
from config import Config

logger = logging.getLogger(__name__)

# Compile regex to extract username (public ID) from LinkedIn profile URL
# Matches:
# - https://www.linkedin.com/in/username
# - https://linkedin.com/in/username/
# - https://www.linkedin.com/in/username?query=params
# - https://www.linkedin.com/in/username/details/experience/
LINKEDIN_URL_REGEX = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_\-\u00C0-\u00FF%]+)"
)

def extract_public_id(url: str) -> Optional[str]:
    """
    Extracts the public profile ID (username) from a LinkedIn URL.
    """
    match = LINKEDIN_URL_REGEX.search(url)
    if match:
        # Decode URL-encoded characters if any (e.g. %C3%A9 -> é)
        from urllib.parse import unquote
        return unquote(match.group(1))
    return None

class LinkedInScraper:
    def __init__(self):
        self.api = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Initializes the open-linkedin-api client using configured authentication method.
        """
        if Config.is_cookie_auth_available():
            logger.info("Initializing LinkedIn client using session cookies...")
            # Create a RequestsCookieJar containing session cookies
            cookie_jar = requests.cookies.RequestsCookieJar()
            cookie_jar.set("li_at", Config.LI_AT, domain=".linkedin.com")
            cookie_jar.set("JSESSIONID", Config.JSESSIONID, domain=".linkedin.com")
            
            # Initialize Linkedin with cookies
            self.api = Linkedin(username="", password="", cookies=cookie_jar)
        elif Config.is_password_auth_available():
            logger.info("Initializing LinkedIn client using username/password...")
            self.api = Linkedin(username=Config.USERNAME, password=Config.PASSWORD)
        else:
            logger.warning("LinkedIn API initialized without credentials. Requests will fail.")
            self.api = None

    def get_client(self) -> Linkedin:
        if not self.api:
            # Try to re-initialize if environment variables were loaded dynamically
            self._initialize_client()
            if not self.api:
                raise ValueError(
                    "LinkedIn authentication credentials not configured in backend. "
                    "Please set LINKEDIN_LI_AT & LINKEDIN_JSESSIONID in the environment."
                )
        return self.api

    def scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Extracts public ID from the URL, fetches profile and contact info,
        and returns a unified structured dictionary.
        """
        public_id = extract_public_id(profile_url)
        if not public_id:
            raise ValueError(f"Invalid LinkedIn profile URL: '{profile_url}'. Match pattern: linkedin.com/in/<username>")

        client = self.get_client()

        logger.info(f"Fetching profile data for public_id: {public_id}...")
        try:
            profile_data = client.get_profile(public_id=public_id)
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            raise RuntimeError(f"Failed to fetch profile '{public_id}' from LinkedIn: {str(e)}")

        if not profile_data:
            raise ValueError(f"Profile '{public_id}' not found or inaccessible. Verify credentials and profile URL.")

        logger.info(f"Successfully fetched profile for {public_id}. Fetching contact info...")
        contact_info = {}
        try:
            contact_data = client.get_profile_contact_info(public_id=public_id)
            if contact_data:
                # Format websites into strings
                websites = []
                for site in contact_data.get("websites", []):
                    url = site.get("url")
                    if url:
                        websites.append(url)
                
                contact_info = {
                    "email": contact_data.get("email_address"),
                    "phone_numbers": contact_data.get("phone_numbers", []),
                    "websites": websites,
                    "twitter": contact_data.get("twitter", []) or [],
                    "birthdate": str(contact_data.get("birthdate")) if contact_data.get("birthdate") else None
                }
        except Exception as e:
            # We don't want to crash the request if contact info fails (e.g. not a 1st degree connection)
            logger.warning(f"Could not fetch contact info for '{public_id}' (often requires 1st-degree connection): {e}")

        # Combine first and last names for a clean full name
        first_name = profile_data.get("firstName", "")
        last_name = profile_data.get("lastName", "")
        full_name = f"{first_name} {last_name}".strip() or public_id

        # Normalize experience items
        normalized_experience = []
        for exp in profile_data.get("experience", []):
            normalized_experience.append({
                "companyName": exp.get("companyName"),
                "companyLogoUrl": exp.get("companyLogoUrl"),
                "title": exp.get("title"),
                "locationName": exp.get("locationName"),
                "description": exp.get("description"),
                "timePeriod": exp.get("timePeriod")
            })

        # Normalize education items
        normalized_education = []
        for edu in profile_data.get("education", []):
            normalized_education.append({
                "schoolName": edu.get("schoolName"),
                "schoolLogoUrl": edu.get("schoolLogoUrl"),
                "degreeName": edu.get("degreeName"),
                "fieldOfStudy": edu.get("fieldOfStudy"),
                "description": edu.get("description"),
                "timePeriod": edu.get("timePeriod")
            })

        # Normalize skills items
        normalized_skills = []
        for skill in profile_data.get("skills", []):
            name = skill.get("name")
            if name:
                normalized_skills.append({"name": name})

        # Normalize certifications
        normalized_certifications = []
        for cert in profile_data.get("certifications", []):
            normalized_certifications.append({
                "name": cert.get("name"),
                "authority": cert.get("authority"),
                "licenseNumber": cert.get("licenseNumber"),
                "timePeriod": cert.get("timePeriod"),
                "url": cert.get("url")
            })

        # Normalize languages
        normalized_languages = []
        for lang in profile_data.get("languages", []):
            normalized_languages.append({
                "name": lang.get("name"),
                "proficiency": lang.get("proficiency")
            })

        # Normalize projects
        normalized_projects = []
        for proj in profile_data.get("projects", []):
            normalized_projects.append({
                "name": proj.get("name"),
                "description": proj.get("description"),
                "url": proj.get("url")
            })

        # Normalize volunteer
        normalized_volunteer = []
        for vol in profile_data.get("volunteer", []):
            normalized_volunteer.append({
                "role": vol.get("role"),
                "companyName": vol.get("companyName"),
                "description": vol.get("description"),
                "timePeriod": vol.get("timePeriod")
            })

        # Normalize honors
        normalized_honors = []
        for honor in profile_data.get("honors", []):
            normalized_honors.append({
                "title": honor.get("title"),
                "issuer": honor.get("issuer"),
                "description": honor.get("description"),
                "issueDate": honor.get("issueDate")
            })

        # Assemble clean profile dictionary
        result = {
            "public_id": public_id,
            "urn_id": profile_data.get("urn_id", ""),
            "firstName": first_name,
            "lastName": last_name,
            "full_name": full_name,
            "headline": profile_data.get("headline"),
            "geoLocationName": profile_data.get("geoLocationName") or profile_data.get("locationName"),
            "summary": profile_data.get("summary"),
            "displayPictureUrl": profile_data.get("displayPictureUrl"),
            "experience": normalized_experience,
            "education": normalized_education,
            "skills": normalized_skills,
            "certifications": normalized_certifications,
            "languages": normalized_languages,
            "projects": normalized_projects,
            "volunteer": normalized_volunteer,
            "honors": normalized_honors,
            "contact_info": contact_info or None
        }

        return result
