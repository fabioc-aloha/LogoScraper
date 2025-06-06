"""Session Management Module

This module provides consistent HTTP session management across services.
"""

import requests
import os
import time
import logging
from src.config import CONFIG

class SessionManager:
    """Handles HTTP session management."""

    def __init__(self, user_agent=None, timeout=None, max_retries=None, retry_delay=None):
        """Initialize session manager.
        
        Args:
            user_agent: Optional custom user agent
            timeout: Optional custom timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        # Use a standard requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or CONFIG['USER_AGENT']
        })
        self.timeout = timeout or CONFIG['REQUEST_TIMEOUT']
        self.max_retries = max_retries or CONFIG.get('MAX_RETRIES', 3)
        self.retry_delay = retry_delay or CONFIG.get('RETRY_DELAY', 1.0)

    def get(self, url, **kwargs):
        """Perform a GET request with consistent settings and retry logic.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get
            
        Returns:
            requests.Response object
        """
        kwargs.setdefault('timeout', self.timeout)
        
        attempt = 0
        last_exception = None
        
        while attempt < self.max_retries:
            try:
                response = self.session.get(url, **kwargs)
                
                # Return immediately on success
                if response.status_code == 200:
                    return response
                
                # For server errors, retry
                if response.status_code >= 500:
                    attempt += 1
                    if attempt < self.max_retries:
                        logging.info(f"Got status code {response.status_code}, retrying ({attempt}/{self.max_retries})...")
                        time.sleep(self.retry_delay * attempt)  # Progressive backoff
                        continue
                
                # For non-server errors like 404, don't retry
                return response
                
            except (requests.ConnectionError, requests.Timeout) as e:
                # Network errors are retryable
                attempt += 1
                last_exception = e
                
                if attempt < self.max_retries:
                    logging.info(f"Connection error: {str(e)}, retrying ({attempt}/{self.max_retries})...")
                    time.sleep(self.retry_delay * attempt)  # Progressive backoff
                else:
                    logging.error(f"Request failed after {self.max_retries} attempts: {str(e)}")
                    raise
        
        # If we get here, we've exhausted retries
        if last_exception:
            raise last_exception
            
        # This shouldn't happen, but just to be safe
        return self.session.get(url, **kwargs)

    def close(self):
        """Close the session safely."""
        try:
            self.session.close()
        except Exception:
            pass  # Ignore errors during cleanup