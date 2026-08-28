# tests/test_client.py
import unittest
from unittest.mock import patch, MagicMock
import httpx
from app.linkedin.client import LinkedInClient
from app.config import Config
from app.exceptions import (
    AuthFailedException,
    AccessDeniedException,
    ProfileNotFoundException,
    RateLimitedException,
    RequestFailedException
)

class TestLinkedInClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Configure env variables for client to pass init check
        Config.LI_AT = "AQED...mockSessionCookie"
        Config.JSESSIONID = "ajax:123456789"
        self.client = LinkedInClient()

    @patch("httpx.AsyncClient.get")
    async def test_client_success_200(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"firstName": "Bill", "lastName": "Gates"}
        mock_get.return_value = mock_response

        res = await self.client.get_raw_profile_view("williamhgates")
        self.assertEqual(res["firstName"], "Bill")
        self.assertEqual(res["lastName"], "Gates")

    @patch("httpx.AsyncClient.get")
    async def test_client_auth_failed_401(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(AuthFailedException):
            await self.client.get_raw_profile_view("williamhgates")

    @patch("httpx.AsyncClient.get")
    async def test_client_access_denied_403(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        with self.assertRaises(AccessDeniedException):
            await self.client.get_raw_profile_view("williamhgates")

    @patch("httpx.AsyncClient.get")
    async def test_client_not_found_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(ProfileNotFoundException):
            await self.client.get_raw_profile_view("williamhgates")

    @patch("httpx.AsyncClient.get")
    async def test_client_rate_limited_429(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        with self.assertRaises(RateLimitedException):
            await self.client.get_raw_profile_view("williamhgates")

    @patch("httpx.AsyncClient.get")
    async def test_client_internal_error_500(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(RequestFailedException):
            await self.client.get_raw_profile_view("williamhgates")

    @patch("httpx.AsyncClient.get")
    async def test_client_timeout_raises_request_failed(self, mock_get):
        mock_get.side_effect = httpx.TimeoutException("Connection timed out")

        with self.assertRaises(RequestFailedException):
            await self.client.get_raw_profile_view("williamhgates")
