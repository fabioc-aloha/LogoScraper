import logging
import pandas as pd
from urllib.parse import urlparse

def clean_url(url):
    """Clean and normalize a URL"""
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
    """Extract domain from URL"""
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