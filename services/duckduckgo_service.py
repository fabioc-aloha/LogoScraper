"""DuckDuckGo Icon Service Integration

This module provides integration with the DuckDuckGo Icon service for fetching
company favicons. It includes rate limiting, error handling, and proper resource
management. This service is used as a fallback when the Clearbit service fails
to provide a suitable logo.

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

class DuckDuckGoService:
    """Service class for fetching icons from the DuckDuckGo Icon service.
    
    This class manages connections to the DuckDuckGo Icon service, handles rate
    limiting, and provides error handling for icon retrieval operations.
    
    Args:
        target_size (int): The desired size of the icon in pixels.
            Note that DuckDuckGo may not return exactly this size.
    
    Attributes:
        target_size (int): The requested icon size in pixels
        session (requests.Session): Reusable session for HTTP requests
    """

    def __init__(self, target_size):
        """Initialize the DuckDuckGo icon service with the target icon size."""
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
    @limits(calls=CONFIG['DUCKDUCKGO_RATE_LIMIT'], period=60)
    def get_logo(self, domain):
        """Fetch a company icon from the DuckDuckGo Icon service.
        
        This method attempts to retrieve a company icon using the domain name.
        It includes automatic rate limiting and retries for failed requests.
        
        Args:
            domain (str): The domain name of the company (e.g., 'example.com')
        
        Returns:
            bytes or None: The icon image data if successful, None if the icon
                could not be retrieved or the domain is invalid.
        
        Note:
            The method automatically handles rate limiting through decorators
            and will sleep if necessary to respect the service's rate limits.
            The returned icon may be in ICO format and require additional
            processing before use.
        """
        if not domain:
            return None
        try:
            url = f'https://icons.duckduckgo.com/ip3/{domain}.ico'
            response = self.session.get(url, timeout=CONFIG['REQUEST_TIMEOUT'])
            if response.status_code == 200:
                return response.content
        except Exception as e:
            logging.error(f"DuckDuckGo favicon service error for {domain}: {str(e)}")
        return None