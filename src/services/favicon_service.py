"""
Favicon Service Integration

This module fetches favicons directly from the target website as a fallback logo source.
If the direct favicon fetch fails, it falls back to DuckDuckGo icons service.

Classes:
- FaviconService: Fetches favicons for a given domain, used when Clearbit fails.

This service provides a secondary online logo source in the scraping pipeline.
"""
import logging
from src.utils.session_manager import SessionManager

class FaviconService:
    """Service class for fetching favicons from the website or DuckDuckGo as fallback."""

    def __init__(self, target_size):
        """Initialize with target size (unused, reserved for future)"""
        self.target_size = target_size
        self.session_manager = SessionManager()

    def get_logo(self, domain):
        """
        Fetch favicon/logo for a domain using both DuckDuckGo and Google S2 services.
        Tries both, returns the largest valid image found. Logs the successful path.
        Returns (logo_bytes, provider, size) or (None, None, None) if not found.
        """
        if not domain:
            return None, None, None
        import requests
        best_logo = None
        best_size = 0
        best_source = None
        # Try DuckDuckGo
        try:
            ddg_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
            response = self.session_manager.get(ddg_url)
            if response.status_code == 200 and response.content:
                if len(response.content) > best_size:
                    best_logo = response.content
                    best_size = len(response.content)
                    best_source = "DuckDuckGo"
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Unrecoverable DNS/domain error for {domain} (DuckDuckGo): {str(e)}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Recoverable HTTP error for {domain} (DuckDuckGo): {str(e)}")
        # Try Google S2
        try:
            google_url = f"https://www.google.com/s2/favicons?domain={domain}"
            response = self.session_manager.get(google_url)
            if response.status_code == 200 and response.content:
                if len(response.content) > best_size:
                    best_logo = response.content
                    best_size = len(response.content)
                    best_source = "Google S2"
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Unrecoverable DNS/domain error for {domain} (Google S2): {str(e)}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Recoverable HTTP error for {domain} (Google S2): {str(e)}")
        if best_logo:
            # Log the size and source for performance analysis
            logging.info(f"FaviconService: Successfully retrieved logo for {domain} from {best_source} (size: {best_size} bytes)")
            return best_logo, best_source, best_size
        return None, None, None

    def close(self):
        """Close the HTTP session."""
        try:
            self.session_manager.close()
        except Exception:
            pass