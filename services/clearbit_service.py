import os
import sys
import logging
import requests
from ratelimit import limits, sleep_and_retry

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

class ClearbitService:
    def __init__(self, target_size):
        self.target_size = target_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': CONFIG['USER_AGENT']
        })

    @sleep_and_retry
    @limits(calls=CONFIG['CLEARBIT_RATE_LIMIT'], period=60)
    def get_logo(self, domain):
        """Get logo from Clearbit Logo API"""
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