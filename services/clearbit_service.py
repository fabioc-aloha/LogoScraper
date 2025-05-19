"""Clearbit Logo Service Integration

This module provides integration with the Clearbit Logo API for fetching company logos.
It includes rate limiting and error handling.
"""

import logging
from utils.rate_limiter import rate_limit
from utils.session_manager import SessionManager
from config import CONFIG

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
                logging.warning(f"ClearbitService: Non-200 response for {domain} (status {response.status_code}). Response content: {response.content[:200]}")
        except Exception as e:
            logging.error(f"Clearbit logo service error for {domain}: {str(e)}")
        return None
        
    def close(self):
        """Close the HTTP session."""
        self.session_manager.close()