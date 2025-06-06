import unittest
from unittest.mock import MagicMock, patch
from services.favicon_service import FaviconService

class TestFaviconService(unittest.TestCase):
    def setUp(self):
        self.service = FaviconService(target_size=32)
        self.domain = "example.com"

    @patch('services.favicon_service.SessionManager')
    def test_get_logo_success_from_common_paths(self, MockSessionManager):
        # Simulate a valid image at the first path
        mock_session = MockSessionManager.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fakeimage1' * 10  # 80 bytes
        mock_session.get.return_value = mock_response
        result = FaviconService(target_size=32).get_logo(self.domain)
        self.assertEqual(result, mock_response.content)

    @patch('services.favicon_service.SessionManager')
    def test_get_logo_success_from_webmanifest(self, MockSessionManager):
        # Simulate no images in common paths, but a valid icon in site.webmanifest
        mock_session = MockSessionManager.return_value
        # First, all direct fetches fail
        fail_response = MagicMock()
        fail_response.status_code = 404
        fail_response.content = b''
        # Then, webmanifest returns a valid icon path
        manifest_response = MagicMock()
        manifest_response.status_code = 200
        manifest_response.content = b'{"icons": [{"src": "/icon-192.png"}]}'
        # The icon fetch returns a valid image
        icon_response = MagicMock()
        icon_response.status_code = 200
        icon_response.content = b'webmanifesticon' * 10
        # Setup side effects for get()
        def get_side_effect(url):
            if url.endswith('site.webmanifest'):
                return manifest_response
            elif url.endswith('icon-192.png'):
                return icon_response
            return fail_response
        mock_session.get.side_effect = get_side_effect
        result = FaviconService(target_size=32).get_logo(self.domain)
        self.assertEqual(result, icon_response.content)

    @patch('services.favicon_service.SessionManager')
    def test_get_logo_fallback_duckduckgo(self, MockSessionManager):
        # All direct and manifest fetches fail, DuckDuckGo returns a logo
        mock_session = MockSessionManager.return_value
        fail_response = MagicMock()
        fail_response.status_code = 404
        fail_response.content = b''
        ddg_response = MagicMock()
        ddg_response.status_code = 200
        ddg_response.content = b'ddgicon' * 10
        def get_side_effect(url):
            if 'duckduckgo.com' in url:
                return ddg_response
            return fail_response
        mock_session.get.side_effect = get_side_effect
        result = FaviconService(target_size=32).get_logo(self.domain)
        self.assertEqual(result, ddg_response.content)

    @patch('services.favicon_service.SessionManager')
    def test_get_logo_fallback_google_s2(self, MockSessionManager):
        # All direct, manifest, and DuckDuckGo fetches fail, Google S2 returns a logo
        mock_session = MockSessionManager.return_value
        fail_response = MagicMock()
        fail_response.status_code = 404
        fail_response.content = b''
        google_response = MagicMock()
        google_response.status_code = 200
        google_response.content = b'googleicon' * 10
        def get_side_effect(url):
            if 'google.com/s2/favicons' in url:
                return google_response
            return fail_response
        mock_session.get.side_effect = get_side_effect
        result = FaviconService(target_size=32).get_logo(self.domain)
        self.assertEqual(result, google_response.content)

    @patch('services.favicon_service.SessionManager')
    def test_get_logo_none_if_all_fail(self, MockSessionManager):
        # All fetches fail
        mock_session = MockSessionManager.return_value
        fail_response = MagicMock()
        fail_response.status_code = 404
        fail_response.content = b''
        mock_session.get.return_value = fail_response
        result = FaviconService(target_size=32).get_logo(self.domain)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
