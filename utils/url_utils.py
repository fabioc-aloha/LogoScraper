"""URL Processing Utilities

This module provides utility functions for processing and normalizing URLs and domain names.
It handles various edge cases and malformed URLs to ensure maximum compatibility with
different URL formats found in company data.

The module includes comprehensive error handling and logging for URL processing failures.
"""

import logging
import pandas as pd
from urllib.parse import urlparse

def clean_url(url):
    """Clean and normalize a URL to a standard format.
    
    This function handles various URL formats and edge cases to produce a
    consistent, usable URL. It performs the following normalizations:
    - Removes whitespace
    - Converts to lowercase
    - Handles comma-separated URLs (takes first)
    - Removes email-style URLs
    - Adds https:// scheme if missing
    
    Args:
        url (str): The URL to clean and normalize
    
    Returns:
        str or None: The normalized URL if successful, None if the URL is
            invalid or empty
    
    Examples:
        >>> clean_url("example.com")
        'https://example.com'
        >>> clean_url("user@example.com")
        'https://user'
        >>> clean_url("example.com, backup.com")
        'https://example.com'
    """
    if not url or pd.isna(url):
        return None
        
    # Convert to string and clean
    url = str(url).strip().lower()
    
    # Handle multiple URLs separated by commas
    if ',' in url:
        urls = [u.strip() for u in url.split(',')]
        url = urls[0]  # Take the first URL
        
    # Remove email-style URLs (with @)
    if '@' in url:
        url = url.split('@')[0]
        
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    return url

def get_domain_from_url(url):
    """Extract and normalize the domain name from a URL.
    
    This function parses URLs and extracts the domain name, performing
    standard normalizations like removing 'www.' prefixes.
    
    Args:
        url (str): The URL to extract the domain from
    
    Returns:
        str or None: The normalized domain name if successful, None if the
            URL is invalid or cannot be parsed
    
    Examples:
        >>> get_domain_from_url("https://www.example.com/path")
        'example.com'
        >>> get_domain_from_url("example.com")
        'example.com'
    
    Note:
        The function automatically cleans the URL using clean_url() before
        extracting the domain.
    """
    if not url or pd.isna(url):
        return None
    try:
        url = clean_url(url)
        if not url:
            return None
            
        parsed = urlparse(url)
        domain = parsed.netloc
        if not domain:
            return None
            
        # Remove www. prefix
        domain = domain.replace('www.', '')
        return domain
    except Exception as e:
        logging.error(f"Error extracting domain from URL {url}: {str(e)}")
        return None