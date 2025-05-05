"""Clearbit Logo Service Integration

This module provides integration with the Clearbit Logo API for fetching company logos.
It includes rate limiting, error handling, and proper resource management.

The service respects rate limits defined in the configuration and provides robust
error handling for network and API issues.
"""

import os
import sys
import logging
import requests
from ratelimit import limits, sleep_and_retry

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

class ClearbitService:
    """Service class for fetching logos from the Clearbit Logo API.
    
    This class manages connections to the Clearbit Logo API, handles rate limiting,
    and provides error handling for logo retrieval operations.
    
    Args:
        target_size (int): The desired size of the logo in pixels.
            The API will attempt to return a logo matching this size.
    
    Attributes:
        target_size (int): The requested logo size in pixels
        session (requests.Session): Reusable session for HTTP requests
    """

    def __init__(self, target_size):
        """Initialize the Clearbit logo service with the target logo size."""
        self.target_size = target_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['USER_AGENT']
        })

    def close(self):
        """Clean up resources used by the service.
        
        This method ensures proper cleanup of network resources by closing
        the requests session. It's designed to be safe to call multiple times
        and handles its own exceptions.
        """
        if hasattr(self, 'session'):
            try:
                self.session.close()
            except:
                pass

    @sleep_and_retry
    @limits(calls=CONFIG['CLEARBIT_RATE_LIMIT'], period=60)
    def get_logo(self, domain):
        """Fetch a company logo from the Clearbit Logo API.
        
        This method attempts to retrieve a company logo using the domain name.
        It includes automatic rate limiting and retries for failed requests.
        
        Args:
            domain (str): The domain name of the company (e.g., 'example.com')
        
        Returns:
            bytes or None: The logo image data if successful, None if the logo
                could not be retrieved or the domain is invalid.
        
        Note:
            The method automatically handles rate limiting through decorators
            and will sleep if necessary to respect the API's rate limits.
        """
        if not domain:
            return None
        try:
            url = f"https://logo.clearbit.com/{domain}?size={self.target_size}"
            response = self.session.get(url, timeout=CONFIG['REQUEST_TIMEOUT'])
            if response.status_code == 200:
                return response.content
        except Exception as e:
            logging.error(f"Clearbit logo service error for {domain}: {str(e)}")
        return None