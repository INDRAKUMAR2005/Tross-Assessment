import unittest
from fastapi.testclient import TestClient
from main import app
from scraper import extract_public_id

class TestLinkedInProfileAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_url_extraction(self):
        """
        Verify that our regex correctly extracts the username from various LinkedIn URL formats.
        """
        valid_urls = [
            ("https://www.linkedin.com/in/williamhgates", "williamhgates"),
            ("https://linkedin.com/in/williamhgates/", "williamhgates"),
            ("https://www.linkedin.com/in/williamhgates?q=param", "williamhgates"),
            ("https://www.linkedin.com/in/williamhgates/details/experience/", "williamhgates"),
            ("http://www.linkedin.com/in/williamhgates", "williamhgates"),
            ("www.linkedin.com/in/williamhgates", "williamhgates"),
            ("linkedin.com/in/williamhgates", "williamhgates")
        ]
        
        invalid_urls = [
            "https://www.linkedin.com/feed/",
            "https://www.linkedin.com/company/microsoft",
            "https://google.com"
        ]

        for url, expected in valid_urls:
            self.assertEqual(extract_public_id(url), expected, f"Failed for url: {url}")

        for url in invalid_urls:
            self.assertIsNone(extract_public_id(url), f"Should fail for url: {url}")

    def test_index_route(self):
        """
        Verify that the root endpoint returns instructions and status.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("documentation", response.json())

    def test_health_route(self):
        """
        Verify that the health check endpoint works.
        """
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

    def test_invalid_profile_url(self):
        """
        Verify that posting an invalid URL returns a 400 Bad Request.
        """
        response = self.client.post("/api/v1/profile", json={"profile_url": "https://google.com"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid LinkedIn profile URL", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
