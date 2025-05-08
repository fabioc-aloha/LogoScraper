"""URL Processing Utilities

This module provides utility functions for processing and normalizing URLs and domain names.
"""

import logging
from urllib.parse import urlparse

def clean_domain(domain):
    """Clean and normalize a domain name."""
    if not domain:
        return None
        
    # Convert to lowercase
    domain = domain.lower()
    
    # Remove common prefixes
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Remove trailing dots and spaces
    domain = domain.strip(' .')
    
    return domain

def get_domain_from_url(url):
    """Extract and normalize the domain name from a URL."""
    if not url:
        return None
        
    try:
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Parse URL and extract domain
        parsed = urlparse(url)
        if parsed.netloc:
            return clean_domain(parsed.netloc)
            
        # Try the path if netloc is empty
        if parsed.path:
            return clean_domain(parsed.path.split('/')[0])
        
        return None
        
    except Exception as e:
        logging.error(f"Error extracting domain from URL {url}: {str(e)}")
        return None