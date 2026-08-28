# app/linkedin/parser.py
import logging
from typing import Dict, Any, Optional, List
from app.exceptions import ResponseStructureChangedException
from app.models.response import (
    ProfileResponse,
    ExperienceItem,
    EducationItem,
    SkillItem,
    CertificationItem,
    LanguageItem,
    ProjectItem,
    VolunteerItem,
    HonorItem,
    ContactInfo,
    TimePeriod,
    DateModel
)

logger = logging.getLogger(__name__)

class LinkedInParser:
    @staticmethod
    def parse_time_period(time_period: Optional[Dict[str, Any]]) -> Optional[TimePeriod]:
        if not time_period:
            return None
            
        start = time_period.get("startDate")
        end = time_period.get("endDate")
        
        start_date = None
        if start:
            start_date = DateModel(year=start.get("year"), month=start.get("month"))
            
        end_date = None
        if end:
            end_date = DateModel(year=end.get("year"), month=end.get("month"))
            
        return TimePeriod(startDate=start_date, endDate=end_date)

    @staticmethod
    def get_localized(field_name: str, block: dict) -> Optional[str]:
        """
        Attempts to read a flat string field, falling back to resolving 
        multiLocale localized equivalents (e.g. multiLocaleFirstName).
        """
        # Try flat string field first
        val = block.get(field_name)
        if isinstance(val, str) and val.strip():
            return val
            
        # Try multiLocale variant
        multi_key = f"multiLocale{field_name[0].upper()}{field_name[1:]}"
        multi_val = block.get(multi_key)
        if isinstance(multi_val, dict):
            # Prioritize standard English locales
            for key in ["en_US", "en"]:
                if key in multi_val and isinstance(multi_val[key], str):
                    return multi_val[key]
            # Fallback to any present locale value
            for val in multi_val.values():
                if isinstance(val, str) and val.strip():
                    return val
        return None

    @classmethod
    def normalize_profile(
        cls, 
        public_id: str, 
        profile_data: Dict[str, Any], 
        contact_data: Optional[Dict[str, Any]] = None
    ) -> ProfileResponse:
        """
        Parses raw nested Voyager/Dash response payloads into the normalized domain profile response structure.
        """
        try:
            # 1. Resolve Profile Block from elements list or root
            elements = profile_data.get("elements", [])
            if isinstance(elements, list) and len(elements) > 0:
                profile_block = elements[0]
            else:
                profile_block = profile_data

            # 2. Extract and validate Name fields
            first_name = cls.get_localized("firstName", profile_block)
            last_name = cls.get_localized("lastName", profile_block)
            full_name = f"{first_name or ''} {last_name or ''}".strip() or public_id

            if not first_name and not last_name:
                # If neither is found, check if it has a fallback name property
                alt_name = profile_block.get("name") or profile_block.get("full_name")
                if alt_name:
                    full_name = alt_name
                else:
                    raise ResponseStructureChangedException("Profile data JSON is missing standard name keys.")

            # Headline & About Summary
            headline = cls.get_localized("headline", profile_block)
            summary = cls.get_localized("summary", profile_block) or profile_block.get("about")
            
            # Location
            location = cls.get_localized("geoLocationName", profile_block) or cls.get_localized("locationName", profile_block)

            # Contact info normalization
            contact_info = None
            if contact_data:
                websites = [site.get("url") for site in contact_data.get("websites", []) if site.get("url")]
                contact_info = ContactInfo(
                    email=contact_data.get("email_address") or contact_data.get("email"),
                    phone_numbers=contact_data.get("phone_numbers", []),
                    websites=websites,
                    twitter=contact_data.get("twitter", []) or [],
                    birthdate=str(contact_data.get("birthdate")) if contact_data.get("birthdate") else None
                )

            # Fetch included array for flattened structures (Dash JSON API format)
            included = profile_data.get("included", [])

            # Experience list normalization
            experiences = []
            exp_source = profile_block.get("experience") or profile_block.get("positions") or profile_data.get("experience") or []
            if not exp_source and included:
                exp_source = [item for item in included if "Position" in item.get("$type", "")]

            for exp in exp_source:
                comp_name = exp.get("companyName")
                if not comp_name and isinstance(exp.get("company"), dict):
                    comp_name = exp.get("company").get("name") or exp.get("company").get("companyName")
                
                comp_logo = exp.get("companyLogoUrl")
                if not comp_logo and isinstance(exp.get("company"), dict):
                    logo_obj = exp.get("company").get("logo")
                    if isinstance(logo_obj, dict):
                        comp_logo = logo_obj.get("rootUrl") or logo_obj.get("companyLogoUrl")

                experiences.append(
                    ExperienceItem(
                        companyName=comp_name,
                        companyLogoUrl=comp_logo,
                        title=exp.get("title"),
                        locationName=exp.get("locationName") or exp.get("location"),
                        description=exp.get("description"),
                        timePeriod=cls.parse_time_period(exp.get("timePeriod"))
                    )
                )

            # Education list normalization
            educations = []
            edu_source = profile_block.get("education") or profile_data.get("education") or []
            if not edu_source and included:
                edu_source = [item for item in included if "Education" in item.get("$type", "")]

            for edu in edu_source:
                school_name = edu.get("schoolName")
                if not school_name and isinstance(edu.get("school"), dict):
                    school_name = edu.get("school").get("schoolName") or edu.get("school").get("name")
                    
                school_logo = edu.get("schoolLogoUrl")
                if not school_logo and isinstance(edu.get("school"), dict):
                    logo_obj = edu.get("school").get("logo")
                    if isinstance(logo_obj, dict):
                        school_logo = logo_obj.get("rootUrl")

                educations.append(
                    EducationItem(
                        schoolName=school_name,
                        schoolLogoUrl=school_logo,
                        degreeName=edu.get("degreeName") or edu.get("degree"),
                        fieldOfStudy=edu.get("fieldOfStudy"),
                        description=edu.get("description"),
                        timePeriod=cls.parse_time_period(edu.get("timePeriod"))
                    )
                )

            # Skills
            skills = []
            skills_source = profile_block.get("skills") or profile_data.get("skills") or []
            if not skills_source and included:
                skills_source = [item for item in included if "Skill" in item.get("$type", "")]

            for sk in skills_source:
                name = sk.get("name")
                if name:
                    skills.append(SkillItem(name=name))

            # Certifications
            certifications = []
            cert_source = profile_block.get("certifications") or profile_data.get("certifications") or []
            if not cert_source and included:
                cert_source = [item for item in included if "Certification" in item.get("$type", "")]

            for cert in cert_source:
                certifications.append(
                    CertificationItem(
                        name=cert.get("name"),
                        authority=cert.get("authority"),
                        licenseNumber=cert.get("licenseNumber"),
                        timePeriod=cls.parse_time_period(cert.get("timePeriod")),
                        url=cert.get("url")
                    )
                )

            # Languages
            languages = []
            lang_source = profile_block.get("languages") or profile_data.get("languages") or []
            if not lang_source and included:
                lang_source = [item for item in included if "Language" in item.get("$type", "")]

            for lang in lang_source:
                languages.append(
                    LanguageItem(
                        name=lang.get("name") or lang.get("language"),
                        proficiency=lang.get("proficiency")
                    )
                )

            # Projects
            projects = []
            proj_source = profile_block.get("projects") or profile_data.get("projects") or []
            if not proj_source and included:
                proj_source = [item for item in included if "Project" in item.get("$type", "")]

            for proj in proj_source:
                projects.append(
                    ProjectItem(
                        name=proj.get("name"),
                        description=proj.get("description"),
                        url=proj.get("url")
                    )
                )

            # Volunteer
            volunteers = []
            vol_source = profile_block.get("volunteer") or profile_data.get("volunteer") or []
            if not vol_source and included:
                vol_source = [item for item in included if "VolunteerExperience" in item.get("$type", "")]

            for vol in vol_source:
                volunteers.append(
                    VolunteerItem(
                        role=vol.get("role"),
                        companyName=vol.get("companyName") or vol.get("company"),
                        description=vol.get("description"),
                        timePeriod=cls.parse_time_period(vol.get("timePeriod"))
                    )
                )

            # Honors
            honors = []
            hon_source = profile_block.get("honors") or profile_data.get("honors") or []
            if not hon_source and included:
                hon_source = [item for item in included if "Honor" in item.get("$type", "")]

            for honor in hon_source:
                issue_date = None
                idate = honor.get("issueDate")
                if idate:
                    issue_date = DateModel(year=idate.get("year"), month=idate.get("month"))
                    
                honors.append(
                    HonorItem(
                        title=honor.get("title"),
                        issuer=honor.get("issuer"),
                        description=honor.get("description"),
                        issueDate=issue_date
                    )
                )

            return ProfileResponse(
                public_id=public_id,
                urn_id=profile_block.get("urn_id") or profile_block.get("urn", "").replace("urn:li:fs_profile:", "").replace("urn:li:member:", ""),
                firstName=first_name,
                lastName=last_name,
                full_name=full_name,
                headline=headline,
                geoLocationName=location,
                summary=summary,
                displayPictureUrl=profile_block.get("displayPictureUrl"),
                experience=experiences,
                education=educations,
                skills=skills,
                certifications=certifications,
                languages=languages,
                projects=projects,
                volunteer=volunteers,
                honors=honors,
                contact_info=contact_info
            )
        except Exception as e:
            if isinstance(e, ResponseStructureChangedException):
                raise e
            logger.error(f"Error parsing raw profile payload: {e}")
            raise ResponseStructureChangedException(
                f"Failed to parse LinkedIn response: structural format changed. Detail: {str(e)}"
            )
