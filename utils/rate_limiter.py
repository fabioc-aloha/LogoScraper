"""Rate Limiting Module

This module provides consistent rate limiting functionality across services.
"""

import time

def rate_limit(max_per_minute):
    """Rate limiting decorator for API calls.
    
    Args:
        max_per_minute: Maximum number of calls allowed per minute
        
    Returns:
        Decorated function with rate limiting
    """
    interval = 60.0 / float(max_per_minute)
    last_call = {}

    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            key = func.__name__
            if key in last_call:
                time_since_last = now - last_call[key]
                if time_since_last < interval:
                    time.sleep(interval - time_since_last)
            result = func(*args, **kwargs)
            last_call[key] = time.time()
            return result
        return wrapper
    return decorator