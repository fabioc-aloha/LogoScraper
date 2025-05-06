"""Company Search Service

This module provides functionality to discover company URLs using company names,
variations, and country context. It uses search engines and business directories
to find the most likely official company website.
"""

import os
import sys
import logging
import re
import time
from functools import wraps
from duckduckgo_search import DDGS

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG
from utils.url_utils import get_domain_from_url, clean_url

def rate_limit(max_per_minute):
    """Rate limiting decorator that works with DDGS."""
    interval = 60.0 / float(max_per_minute)
    last_call = {}

    def decorator(func):
        @wraps(func)
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

class CompanySearchService:
    """Service for discovering company URLs through various search methods."""
    
    def __init__(self):
        """Initialize the company search service."""
        self.ddgs = DDGS()
        self.tld_map = {
            'United States': 'com',
            'United Kingdom': 'co.uk',
            'Australia': 'com.au',
            'Canada': 'ca',
            'Germany': 'de',
            'France': 'fr',
            'Italy': 'it',
            'Spain': 'es',
            'Netherlands': 'nl',
            'Brazil': 'com.br',
            'India': 'in',
            'Japan': 'co.jp',
            'China': 'cn',
            'Russia': 'ru',
            'South Korea': 'kr'
        }

    def _get_name_variations(self, company_name):
        """Generate variations of company name for searching."""
        variations = [company_name]
        
        # Remove legal entity types
        legal_entities = [
            ' LLC', ' Inc', ' Ltd', ' Limited', ' Corp', ' Corporation',
            ' GmbH', ' AG', ' SA', ' SL', ' BV', ' NV', ' PLC', ' Co',
            ' PTY', ' LTD', ' Company', ',', '.'
        ]
        clean_name = company_name
        for entity in legal_entities:
            clean_name = re.sub(f'{entity}\\b', '', clean_name, flags=re.IGNORECASE)
        clean_name = clean_name.strip()
        if clean_name != company_name:
            variations.append(clean_name)
            
        # Add 'company' and 'official' keywords
        variations.append(f"{clean_name} company")
        variations.append(f"{clean_name} official website")
        variations.append(f"{clean_name} corporate")
        
        return variations

    @rate_limit(CONFIG['DUCKDUCKGO_RATE_LIMIT'])
    def _search_ddg(self, query):
        """Perform a rate-limited DuckDuckGo search."""
        try:
            results = list(self.ddgs.text(query, max_results=5))
            return results
        except Exception as e:
            logging.error(f"DuckDuckGo search error for query '{query}': {str(e)}")
            return []

    def discover_url(self, company_name, country=None):
        """Discover company URL using search and validation."""
        if not company_name:
            return None
            
        try:
            variations = self._get_name_variations(company_name)
            
            # Add country context if available
            site_filter = ""
            if country and country in self.tld_map:
                site_filter = f"site:.{self.tld_map[country]}"
            
            # Try each variation
            for query in variations:
                search_query = f"{query} {site_filter}".strip()
                logging.info(f"Searching for URL with query: {search_query}")
                
                results = self._search_ddg(search_query)
                if not results:
                    continue
                    
                # Process and validate results
                for result in results:
                    url = clean_url(result.get('link'))
                    if not url:
                        continue
                        
                    # Skip common non-company sites
                    domain = get_domain_from_url(url)
                    if domain and not any(x in domain for x in [
                        'linkedin.com', 'facebook.com', 'twitter.com',
                        'youtube.com', 'bloomberg.com', 'reuters.com',
                        'wikipedia.org', 'crunchbase.com', 'zoominfo.com',
                        'hoovers.com', 'glassdoor.com', 'indeed.com'
                    ]):
                        logging.info(f"Found potential URL for {company_name}: {url}")
                        return url
                        
            logging.warning(f"No suitable URL found for {company_name}")
            return None
            
        except Exception as e:
            logging.error(f"Error discovering URL for {company_name}: {str(e)}")
            return None