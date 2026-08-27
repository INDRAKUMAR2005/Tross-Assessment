from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

# --- Request Schemas ---

class ProfileRequest(BaseModel):
    profile_url: str = Field(
        ..., 
        description="The full LinkedIn profile URL (e.g. https://www.linkedin.com/in/williamhgates/)",
        examples=["https://www.linkedin.com/in/williamhgates/"]
    )


# --- Response Schemas ---

class DateModel(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None

class TimePeriod(BaseModel):
    start_date: Optional[DateModel] = Field(None, alias="startDate")
    end_date: Optional[DateModel] = Field(None, alias="endDate")

class ExperienceItem(BaseModel):
    company_name: Optional[str] = Field(None, alias="companyName")
    company_logo_url: Optional[str] = Field(None, alias="companyLogoUrl")
    title: Optional[str] = None
    location: Optional[str] = Field(None, alias="locationName")
    description: Optional[str] = None
    time_period: Optional[TimePeriod] = Field(None, alias="timePeriod")

class EducationItem(BaseModel):
    school_name: Optional[str] = Field(None, alias="schoolName")
    school_logo_url: Optional[str] = Field(None, alias="schoolLogoUrl")
    degree: Optional[str] = Field(None, alias="degreeName")
    field_of_study: Optional[str] = Field(None, alias="fieldOfStudy")
    description: Optional[str] = None
    time_period: Optional[TimePeriod] = Field(None, alias="timePeriod")

class SkillItem(BaseModel):
    name: str

class CertificationItem(BaseModel):
    name: Optional[str] = None
    authority: Optional[str] = None
    license_number: Optional[str] = Field(None, alias="licenseNumber")
    time_period: Optional[TimePeriod] = Field(None, alias="timePeriod")
    url: Optional[str] = None

class LanguageItem(BaseModel):
    name: Optional[str] = None
    proficiency: Optional[str] = None

class ProjectItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

class VolunteerItem(BaseModel):
    role: Optional[str] = None
    company_name: Optional[str] = Field(None, alias="companyName")
    description: Optional[str] = None
    time_period: Optional[TimePeriod] = Field(None, alias="timePeriod")

class HonorItem(BaseModel):
    title: Optional[str] = None
    issuer: Optional[str] = None
    description: Optional[str] = None
    issue_date: Optional[DateModel] = Field(None, alias="issueDate")

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone_numbers: List[str] = Field(default_factory=list)
    websites: List[str] = Field(default_factory=list)
    twitter: List[str] = Field(default_factory=list)
    birthdate: Optional[str] = None

class ProfileResponse(BaseModel):
    public_id: str = Field(..., description="The LinkedIn public identifier")
    urn_id: str = Field(..., description="The unique LinkedIn URN ID")
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    full_name: str = Field(..., description="Combined first and last name")
    headline: Optional[str] = None
    location: Optional[str] = Field(None, alias="geoLocationName")
    about: Optional[str] = Field(None, alias="summary")
    profile_image_url: Optional[str] = Field(None, alias="displayPictureUrl")
    
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[SkillItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    languages: List[LanguageItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    volunteer: List[VolunteerItem] = Field(default_factory=list)
    honors: List[HonorItem] = Field(default_factory=list)
    contact_info: Optional[ContactInfo] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "public_id": "williamhgates",
                "urn_id": "ACoAAA8WYHgB-AW9gDq...",
                "first_name": "Bill",
                "last_name": "Gates",
                "full_name": "Bill Gates",
                "headline": "Co-chair, Bill & Melinda Gates Foundation",
                "location": "Seattle, Washington, United States",
                "about": "Co-chair of the Bill & Melinda Gates Foundation...",
                "profile_image_url": "https://media.licdn.com/dms/image/...",
                "experience": [
                    {
                        "company_name": "Bill & Melinda Gates Foundation",
                        "title": "Co-chair",
                        "location": "Seattle, WA",
                        "time_period": {
                            "startDate": {"year": 2000, "month": 1}
                        }
                    }
                ],
                "education": [
                    {
                        "school_name": "Harvard University",
                        "degree": "Honorary Doctor of Laws",
                        "time_period": {
                            "startDate": {"year": 1973},
                            "endDate": {"year": 1975}
                        }
                    }
                ],
                "skills": [
                    {"name": "Philanthropy"},
                    {"name": "Technology"}
                ],
                "certifications": [],
                "languages": [
                    {"name": "English", "proficiency": "Native or bilingual proficiency"}
                ],
                "projects": [],
                "volunteer": [],
                "honors": [],
                "contact_info": {
                    "email": None,
                    "phone_numbers": [],
                    "websites": ["https://www.gatesnotes.com"],
                    "twitter": [],
                    "birthdate": None
                }
            }
        }
