"""Search Cache Module

This module handles caching of URL search results.
"""

import logging
import json
import os
from config import CONFIG

class SearchCache:
    """Handles caching of search results."""

    def __init__(self, cache_file=None):
        """Initialize the search cache."""
        if cache_file is None:
            cache_file = os.path.join(CONFIG['TEMP_FOLDER'], 'search_cache.json')
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading search cache: {str(e)}")
                return {}
        return {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logging.error(f"Error saving search cache: {str(e)}")

    def get(self, key):
        """Get a cached result."""
        return self.cache.get(key)

    def set(self, key, value):
        """Set a cache entry and save to disk."""
        self.cache[key] = value
        self._save_cache()

    def has(self, key):
        """Check if key exists in cache."""
        return key in self.cache