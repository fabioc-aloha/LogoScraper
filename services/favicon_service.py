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
    def __init__(self, target_size):
        self.target_size = target_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['USER_AGENT']
        })

    @sleep_and_retry
    @limits(calls=CONFIG['FAVICON_RATE_LIMIT'], period=60)
    def get_logo(self, domain):
        """Get favicon from domain"""
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