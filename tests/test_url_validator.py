# tests/test_url_validator.py
import unittest
from app.utils.url_validator import LinkedInProfileIdentifier
from app.exceptions import InvalidProfileURLException

class TestURLValidator(unittest.TestCase):
    def test_valid_urls(self):
        valid_cases = [
            ("https://www.linkedin.com/in/williamhgates", "williamhgates"),
            ("https://linkedin.com/in/williamhgates/", "williamhgates"),
            ("https://www.linkedin.com/in/williamhgates?q=param", "williamhgates"),
            ("https://www.linkedin.com/in/williamhgates/details/experience/", "williamhgates"),
            ("http://www.linkedin.com/in/williamhgates", "williamhgates"),
            ("www.linkedin.com/in/williamhgates", "williamhgates"),
            ("linkedin.com/in/williamhgates", "williamhgates"),
            ("https://www.linkedin.com/in/john-doe-123%C3%A9", "john-doe-123é")
        ]
        
        for url, expected in valid_cases:
            self.assertEqual(
                LinkedInProfileIdentifier.extract_public_id(url),
                expected,
                f"Failed validation/extraction for URL: {url}"
            )

    def test_invalid_urls(self):
        invalid_cases = [
            "",
            "https://www.linkedin.com/feed/",
            "https://www.linkedin.com/company/microsoft",
            "https://google.com"
        ]
        
        for url in invalid_cases:
            with self.assertRaises(InvalidProfileURLException):
                LinkedInProfileIdentifier.extract_public_id(url)
