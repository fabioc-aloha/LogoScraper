"""
Favicon Service Integration
Fetches a favicon from DuckDuckGo icons service as ICO and returns raw bytes.
"""
import logging
from utils.session_manager import SessionManager
from config import CONFIG

class FaviconService:
    """Service class for fetching favicons via DuckDuckGo icon URL."""

    def __init__(self, target_size):
        """Initialize with target size (unused, reserved for future)"""
        self.target_size = target_size
        self.session_manager = SessionManager()

    def get_logo(self, domain):
        """Fetch favicon for a domain using DuckDuckGo icons service."""
        if not domain:
            return None
        try:
            # Direct favicon URL
            url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
            response = self.session_manager.get(url)
            if response.status_code == 200 and response.content:
                return response.content
        except Exception as e:
            logging.error(f"Favicon service error for {domain}: {str(e)}")
        return None

    def close(self):
        """Close the HTTP session."""
        try:
            self.session_manager.close()
        except Exception:
            pass