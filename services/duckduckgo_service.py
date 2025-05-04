import logging
import requests
from ratelimit import limits, sleep_and_retry

FAVICON_RATE_LIMIT = 1800  # 30 requests per second

class DuckDuckGoService:
    def __init__(self, target_size):
        self.target_size = target_size
        self.session = requests.Session()

    @sleep_and_retry
    @limits(calls=FAVICON_RATE_LIMIT, period=60)
    def get_logo(self, domain):
        """Get logo from DuckDuckGo favicon service"""
        if not domain:
            return None
        try:
            url = f'https://icons.duckduckgo.com/ip3/{domain}.ico'
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            logging.error(f"DuckDuckGo favicon service error for {domain}: {str(e)}")
        return None