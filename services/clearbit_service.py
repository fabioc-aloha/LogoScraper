import logging
import requests
from ratelimit import limits, sleep_and_retry

CLEARBIT_RATE_LIMIT = 3600  # 60 requests per second

class ClearbitService:
    def __init__(self, target_size):
        self.target_size = target_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    @sleep_and_retry
    @limits(calls=CLEARBIT_RATE_LIMIT, period=60)
    def get_logo(self, domain):
        """Get logo from Clearbit Logo API"""
        if not domain:
            return None
        try:
            url = f"https://logo.clearbit.com/{domain}?size={self.target_size}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            logging.error(f"Clearbit logo service error for {domain}: {str(e)}")
        return None