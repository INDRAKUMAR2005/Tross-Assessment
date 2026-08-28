# app/models/request.py
from pydantic import BaseModel, Field

class ProfileRequest(BaseModel):
    profile_url: str = Field(
        ...,
        description="The full LinkedIn profile URL (e.g. https://www.linkedin.com/in/williamhgates/)",
        examples=["https://www.linkedin.com/in/williamhgates/"]
    )
