"""Favicon Service Integration

This module provides functionality to fetch favicons directly from company websites.
It serves as an additional fallback when other logo services fail. The service
checks multiple common favicon locations and validates image quality before accepting
a favicon.

The service includes:
- Multiple favicon location checking
- Image size validation
- Rate limiting
- Error handling
"""

import os
import sys
import logging
import requests
from io import BytesIO
from PIL import Image
from ratelimit import limits, sleep_and_retry

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

class FaviconService:
    """Service class for fetching favicons from company websites.
    
    This class handles direct favicon retrieval from company domains, checking
    multiple common locations and validating image quality before accepting
    a favicon as suitable for use.
    
    Args:
        target_size (int): The desired size of the favicon in pixels.
            Used for reference only, as favicons are typically fixed size.
    
    Attributes:
        target_size (int): The requested favicon size in pixels
        session (requests.Session): Reusable session for HTTP requests
    """

    def __init__(self, target_size):
        """Initialize the favicon service with the target size."""
        self.target_size = target_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['USER_AGENT']
        })

    @sleep_and_retry
    @limits(calls=CONFIG['FAVICON_RATE_LIMIT'], period=60)
    def get_logo(self, domain):
        """Fetch a favicon from a company's website.
        
        This method attempts to retrieve a favicon by checking multiple common
        locations on the company's domain. It validates image size and quality
        before accepting a favicon.
        
        Args:
            domain (str): The domain name of the company (e.g., 'example.com')
        
        Returns:
            bytes or None: The favicon image data if a suitable favicon is found,
                None if no valid favicon could be retrieved.
        
        The method checks multiple locations in order:
        1. Standard favicon locations (favicon.ico, favicon.png)
        2. Apple touch icons
        3. Microsoft tile icons
        4. Android chrome icons
        
        Size validation ensures the favicon meets minimum quality requirements.
        """
        if not domain:
            return None
            
        try:
            # Try common favicon locations
            favicon_locations = [f"https://{domain}{path}" for path in CONFIG['FAVICON_LOCATIONS']]

            for url in favicon_locations:
                try:
                    response = self.session.get(url, timeout=CONFIG['REQUEST_TIMEOUT'])
                    if response.status_code == 200:
                        # Verify it's a valid image and check size
                        img = Image.open(BytesIO(response.content))
                        # Get largest dimension for size check
                        max_dimension = max(img.size)
                        if max_dimension >= CONFIG['FAVICON_MIN_SIZE']:
                            return response.content
                except Exception as e:
                    logging.debug(f"Failed to fetch or validate favicon from {url}: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"Favicon service error for {domain}: {str(e)}")
            
        return None