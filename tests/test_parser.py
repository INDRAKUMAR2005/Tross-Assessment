# tests/test_parser.py
import os
import json
import unittest
from app.linkedin.parser import LinkedInParser
from app.exceptions import ResponseStructureChangedException

class TestLinkedInParser(unittest.TestCase):
    def setUp(self):
        fixture_path = os.path.join(
            os.path.dirname(__file__), 
            "fixtures", 
            "profile_response.json"
        )
        with open(fixture_path, "r", encoding="utf-8") as f:
            self.mock_data = json.load(f)

    def test_parser_normalisation(self):
        # Contact info payload mock
        mock_contact = {
            "email_address": "bill.gates@example.com",
            "phone_numbers": [],
            "websites": [{"url": "https://www.gatesnotes.com"}],
            "twitter": [],
            "birthdate": "1955-10-28"
        }
        
        response = LinkedInParser.normalize_profile(
            public_id="williamhgates",
            profile_data=self.mock_data,
            contact_data=mock_contact
        )
        
        # Verify basic values
        self.assertEqual(response.public_id, "williamhgates")
        self.assertEqual(response.first_name, "Bill")
        self.assertEqual(response.last_name, "Gates")
        self.assertEqual(response.full_name, "Bill Gates")
        self.assertEqual(response.headline, "Co-chair, Bill & Melinda Gates Foundation")
        self.assertEqual(response.location, "Seattle, Washington, United States")
        self.assertEqual(response.about, "Co-chair of the Bill & Melinda Gates Foundation...")
        self.assertEqual(response.profile_image_url, "https://media.licdn.com/dms/image/v2/...")

        # Verify experience parsing
        self.assertEqual(len(response.experience), 1)
        exp = response.experience[0]
        self.assertEqual(exp.company_name, "Bill & Melinda Gates Foundation")
        self.assertEqual(exp.title, "Co-chair")
        self.assertEqual(exp.location, "Seattle, WA")
        self.assertEqual(exp.time_period.start_date.year, 2000)
        self.assertEqual(exp.time_period.start_date.month, 1)
        self.assertIsNone(exp.time_period.end_date)

        # Verify education parsing
        self.assertEqual(len(response.education), 1)
        edu = response.education[0]
        self.assertEqual(edu.school_name, "Harvard University")
        self.assertEqual(edu.degree, "Honorary Doctor of Laws")
        self.assertEqual(edu.time_period.start_date.year, 1973)
        self.assertEqual(edu.time_period.end_date.year, 1975)

        # Verify skills
        self.assertEqual(len(response.skills), 2)
        self.assertEqual(response.skills[0].name, "Philanthropy")
        self.assertEqual(response.skills[1].name, "Software Development")

        # Verify certifications
        self.assertEqual(len(response.certifications), 1)
        cert = response.certifications[0]
        self.assertEqual(cert.name, "Certified Professional Scraper")
        self.assertEqual(cert.authority, "Scraper Corp")
        self.assertEqual(cert.license_number, "CPS-12345")
        self.assertEqual(cert.time_period.start_date.year, 2020)
        self.assertEqual(cert.time_period.start_date.month, 5)

        # Verify languages
        self.assertEqual(len(response.languages), 1)
        self.assertEqual(response.languages[0].name, "English")
        self.assertEqual(response.languages[0].proficiency, "Native or bilingual proficiency")

        # Verify contact details
        self.assertIsNotNone(response.contact_info)
        self.assertEqual(response.contact_info.email, "bill.gates@example.com")
        self.assertEqual(response.contact_info.websites, ["https://www.gatesnotes.com"])
        self.assertEqual(response.contact_info.birthdate, "1955-10-28")

    def test_malformed_payload_raises_exception(self):
        malformed_data = {
            "invalidKey": "No name variables present here"
        }
        with self.assertRaises(ResponseStructureChangedException):
            LinkedInParser.normalize_profile(
                public_id="williamhgates",
                profile_data=malformed_data
            )
