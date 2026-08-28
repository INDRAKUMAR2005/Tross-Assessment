# tests/test_profile.py
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.config import Config

class TestProfileEndpoint(unittest.TestCase):
    def setUp(self):
        # Configure variables so that Config.validate() succeeds and API key is off by default
        Config.LI_AT = "AQED...mockSessionCookie"
        Config.JSESSIONID = "ajax:123456789"
        Config.API_KEY_ENABLED = False
        self.client = TestClient(app)

    @patch("app.linkedin.client.LinkedInClient.get_raw_profile_view")
    @patch("app.linkedin.client.LinkedInClient.get_raw_contact_info")
    def test_scrape_profile_success(self, mock_contact, mock_profile):
        mock_profile.return_value = {
            "firstName": "Bill",
            "lastName": "Gates",
            "publicIdentifier": "williamhgates",
            "urn_id": "ACoAAA8WYHgB-AW9gDq...",
            "headline": "Co-chair, Bill & Melinda Gates Foundation",
            "locationName": "Seattle, WA",
            "summary": "Co-chair bio summary details.",
            "displayPictureUrl": "https://media.licdn.com/dms/image/..."
        }
        mock_contact.return_value = {
            "email_address": "bill.gates@example.com",
            "phone_numbers": [],
            "websites": [{"url": "https://gatesnotes.com"}],
            "twitter": [],
            "birthdate": None
        }

        # Request payload
        payload = {"profile_url": "https://www.linkedin.com/in/williamhgates/"}
        
        # Call both mounted routes to ensure compliance
        routes = ["/api/v1/linkedin/profile", "/api/v1/profile"]
        for route in routes:
            response = self.client.post(route, json=payload)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["public_id"], "williamhgates")
            self.assertEqual(data["firstName"], "Bill")
            self.assertEqual(data["lastName"], "Gates")
            self.assertEqual(data["full_name"], "Bill Gates")
            self.assertEqual(data["headline"], "Co-chair, Bill & Melinda Gates Foundation")
            self.assertEqual(data["contact_info"]["email"], "bill.gates@example.com")

    def test_invalid_url_raises_400(self):
        payload = {"profile_url": "https://google.com"}
        response = self.client.post("/api/v1/linkedin/profile", json=payload)
        self.assertEqual(response.status_code, 400)
        
        detail = response.json()["detail"]
        self.assertFalse(detail["success"])
        self.assertEqual(detail["error"]["code"], "INVALID_LINKEDIN_URL")

    @patch("app.linkedin.client.LinkedInClient.get_raw_profile_view")
    def test_profile_not_found_raises_404(self, mock_profile):
        from app.exceptions import ProfileNotFoundException
        mock_profile.side_effect = ProfileNotFoundException("Profile not found.")
        
        payload = {"profile_url": "https://www.linkedin.com/in/nonexistent/"}
        response = self.client.post("/api/v1/linkedin/profile", json=payload)
        self.assertEqual(response.status_code, 404)
        
        detail = response.json()["detail"]
        self.assertFalse(detail["success"])
        self.assertEqual(detail["error"]["code"], "PROFILE_NOT_FOUND")

    @patch("app.linkedin.client.LinkedInClient.get_raw_profile_view")
    def test_rate_limited_raises_429(self, mock_profile):
        from app.exceptions import RateLimitedException
        mock_profile.side_effect = RateLimitedException()
        
        payload = {"profile_url": "https://www.linkedin.com/in/williamhgates/"}
        response = self.client.post("/api/v1/linkedin/profile", json=payload)
        self.assertEqual(response.status_code, 429)
        
        detail = response.json()["detail"]
        self.assertFalse(detail["success"])
        self.assertEqual(detail["error"]["code"], "LINKEDIN_RATE_LIMITED")
