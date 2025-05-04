import os
import sys
import logging
import requests
from ratelimit import limits, sleep_and_retry

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

class DuckDuckGoService:
    def __init__(self, target_size):
        self.target_size = target_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['USER_AGENT']
        })

    @sleep_and_retry
    @limits(calls=CONFIG['DUCKDUCKGO_RATE_LIMIT'], period=60)
    def get_logo(self, domain):
        """Get logo from DuckDuckGo favicon service"""
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