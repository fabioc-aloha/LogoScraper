"""URL Processing Utilities

This module provides utility functions for processing and normalizing URLs and domain names.
It handles various edge cases and malformed URLs to ensure maximum compatibility with
different URL formats found in company data.

The module includes comprehensive error handling and logging for URL processing failures.
"""

import logging
import pandas as pd
import re
from urllib.parse import urlparse

def extract_domain_from_string(text):
    """Extract a domain name from a raw string using pattern matching.
    
    This is a fallback method that attempts to find domain-like patterns
    in strings when standard URL parsing fails.
    
    Args:
        text (str): Raw text that might contain a domain name
        
    Returns:
        str or None: Extracted domain name if found, None otherwise
    """
    if not text or not isinstance(text, str):
        return None
        
    # Remove any email parts (everything before @)
    if '@' in text:
        text = text.split('@')[-1]
    
    # Common domain patterns
    patterns = [
        # Standard domain pattern
        r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})',
        # Domain without scheme or path
        r'([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,})',
        # IP addresses
        r'(?:https?://)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
            
    return None

def clean_domain(domain):
    """Clean and normalize a domain name.
    
    Args:
        domain (str): Domain name to clean
        
    Returns:
        str: Cleaned domain name
    """
    if not domain:
        return None
        
    # Convert to lowercase
    domain = domain.lower()
    
    # Remove common prefixes
    for prefix in ['www.', 'www2.', 'www3.', 'ww2.']:
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    
    # Remove trailing dots and spaces
    domain = domain.strip(' .')
    
    # Handle specific known patterns
    domain = re.sub(r'/$', '', domain)  # Remove trailing slash
    domain = re.sub(r':80/?$', '', domain)  # Remove port 80
    domain = re.sub(r':443/?$', '', domain)  # Remove port 443
    
    return domain if domain else None

def clean_url(url):
    """Clean and normalize a URL.
    
    Args:
        url (str): URL to clean
        
    Returns:
        str or None: Cleaned URL if valid, None otherwise
    """
    if not url or pd.isna(url):
        return None
        
    try:
        # Handle multiple URLs (take the first one)
        urls = str(url).split()
        if not urls:
            return None
        url = urls[0]
        
        # Remove email-style URLs (with @)
        if '@' in url:
            url = url.split('@')[-1]
            
        # Clean up whitespace and common issues
        url = url.strip()
        url = re.sub(r'\s+', '', url)
        
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        return url
    except Exception as e:
        logging.error(f"Error cleaning URL {url}: {str(e)}")
        return None

def get_domain_from_url(url):
    """Extract and normalize the domain name from a URL.
    
    This function attempts multiple methods to extract a valid domain name,
    falling back to progressively more lenient parsing if strict methods fail.
    
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
        >>> get_domain_from_url("Visit us at example.com!")
        'example.com'
    """
    if not url or pd.isna(url):
        return None
        
    try:
        # Method 1: Try standard URL parsing
        cleaned_url = clean_url(url)
        if cleaned_url:
            parsed = urlparse(cleaned_url)
            if parsed.netloc:
                domain = clean_domain(parsed.netloc)
                if domain:
                    return domain
                    
            # Try the path if netloc is empty (handle cases like "example.com/path")
            if parsed.path and not parsed.netloc:
                domain = clean_domain(parsed.path.split('/')[0])
                if domain:
                    return domain
                    
        # Method 2: Try direct domain extraction from the original string
        domain = extract_domain_from_string(str(url))
        if domain:
            return clean_domain(domain)
            
        return None
        
    except Exception as e:
        logging.error(f"Error extracting domain from URL {url}: {str(e)}")
        return None