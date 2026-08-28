# app/linkedin/endpoints.py

class LinkedInEndpoints:
    BASE_URL = "https://www.linkedin.com/voyager/api"
    
    @classmethod
    def profile_view(cls, public_id: str) -> str:
        # Voyager Dash endpoint that supports memberIdentity lookup
        return f"{cls.BASE_URL}/identity/dash/profiles?q=memberIdentity&memberIdentity={public_id}"
        
    @classmethod
    def contact_info(cls, public_id: str) -> str:
        # Voyager profile contact info endpoint
        return f"{cls.BASE_URL}/identity/profiles/{public_id}/profileContactInfo"
