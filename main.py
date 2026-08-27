from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import ProfileRequest, ProfileResponse
from scraper import LinkedInScraper
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI App with professional metadata
app = FastAPI(
    title="LinkedIn Profile Scraper API",
    description=(
        "A professional, hosted API that reverse-engineers LinkedIn internal endpoints "
        "to extract detailed profile information (experiences, education, skills, certifications, "
        "languages, and contact details) as structured JSON."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper instance lazily
scraper = LinkedInScraper()

@app.get("/", status_code=status.HTTP_200_OK, include_in_schema=False)
def index():
    return {
        "message": "Welcome to the LinkedIn Profile Scraper API!",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def health():
    """
    Checks the configuration health of the API (whether LinkedIn credentials are set).
    """
    cookie_auth = Config.is_cookie_auth_available()
    password_auth = Config.is_password_auth_available()
    
    if not cookie_auth and not password_auth:
        return {
            "status": "unconfigured",
            "message": "LinkedIn credentials are not set. API calls will fail.",
            "auth_method_configured": None
        }
        
    return {
        "status": "healthy",
        "message": "API is configured and ready.",
        "auth_method_configured": "cookies" if cookie_auth else "credentials"
    }

@app.post(
    "/api/v1/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    tags=["LinkedIn Scraper"],
    summary="Scrape LinkedIn Profile Data",
    response_description="Clean, structured JSON representation of the LinkedIn profile."
)
def get_linkedin_profile(payload: ProfileRequest):
    """
    Accepts a LinkedIn profile URL, extracts details such as name, headline, location, about, 
    experiences, education, skills, certifications, languages, and profile images, 
    and returns them as structured JSON.
    """
    try:
        data = scraper.scrape_profile(payload.profile_url)
        return data
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Runtime scraper error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED if "authenticate" in str(e).lower() or "credentials" in str(e).lower() else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    # Start server locally
    uvicorn.run("main:app", host=Config.HOST, port=Config.PORT, reload=True)
