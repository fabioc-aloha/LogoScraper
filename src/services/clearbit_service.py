"""Clearbit Logo Service Integration

This module provides integration with the Clearbit Logo API for fetching company logos.
It includes rate limiting, error handling, and session management.

Classes:
- ClearbitService: Fetches logos from Clearbit, handles HTTP errors, and manages API rate limits.

This service is the primary online source for company logos in the scraping pipeline.
"""

import logging
import requests
from src.utils.rate_limiter import rate_limit
from src.utils.session_manager import SessionManager
from src.config import CONFIG

class ClearbitService:
    """Service class for fetching logos from the Clearbit Logo API."""
    
    def __init__(self, target_size):
        """Initialize the Clearbit logo service with the target logo size."""
        self.target_size = target_size
        self.session_manager = SessionManager()

    @rate_limit(CONFIG['CLEARBIT_RATE_LIMIT'])
    def get_logo(self, domain):
        """Fetch a company logo from the Clearbit Logo API."""
        if not domain:
            logging.warning("ClearbitService: No domain provided.")
            return None
        try:
            url = f"{CONFIG['CLEARBIT_BASE_URL']}/{domain}?size={self.target_size}"
            response = self.session_manager.get(url)
            if response.status_code == 200:
                return response.content
            else:
                # Move expected failures to info
                if response.status_code in (403, 404):
                    logging.info(f"ClearbitService: Non-200 response for {domain} (status {response.status_code})")
                else:
                    logging.warning(f"ClearbitService: Unexpected non-200 response for {domain} (status {response.status_code})")
        except requests.exceptions.Timeout:
            logging.info(f"ClearbitService: Timeout for {domain}")
            return None
        except requests.exceptions.ConnectionError:
            logging.info(f"ClearbitService: Connection error for {domain}")
            return None
        except Exception as e:
            logging.error(f"ClearbitService: Unexpected error for {domain}: {e}")
            return None
        return None
        
    def close(self):
        """Close the HTTP session."""
        self.session_manager.close()