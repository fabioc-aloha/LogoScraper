"""URL Processing Utilities

This module provides utility functions for processing and normalizing URLs and domain names.

Functions:
- clean_domain(domain): Cleans and normalizes a domain string, handling unwanted characters, delimiters, prefixes, and edge cases.
- get_domain_from_url(url_or_domain): Extracts and cleans the domain from a URL or domain string, robust to malformed or email-like input.

These utilities are used throughout the logo scraping pipeline to ensure only valid, clean domains are used for logo retrieval.
"""

import re
from urllib.parse import urlparse

def clean_domain(domain):
    """Clean and normalize a domain name.
    - Lowercase
    - Remove common prefixes (www.)
    - Remove unwanted characters (commas, semicolons, slashes, backslashes, quotes, angle brackets, parentheses, etc.)
    - Handle multiple domains separated by common delimiters (use only the first valid one)
    - Remove anything after '@'
    - Remove leading/trailing dots and hyphens
    - Strip spaces
    - Validate minimum domain requirements
    """
    if not domain:
        return None

    # Remove anything before '@' (e.g. user@domain.com -> domain.com)
    domain = domain.split('@')[-1]

    # Split on common delimiters and use the first non-empty part
    delimiters = r'[;,/\\\s]'
    parts = [p for p in re.split(delimiters, domain) if p]
    domain = parts[0] if parts else domain

    # Remove unwanted characters
    domain = re.sub(r'["\'<>\(\)\[\]]', '', domain)

    # Remove common prefixes
    domain = domain.lower()
    if domain.startswith('www.'):
        domain = domain[4:]

    # Remove leading/trailing dots and hyphens and spaces
    domain = domain.strip(' .-')

    # Basic domain validation - must be at least 4 characters and contain a dot
    if not domain or len(domain) < 4 or '.' not in domain:
        return None
    
    # Additional validation - ensure it's not just a single character or obvious invalid domain
    parts = domain.split('.')
    if len(parts) < 2 or any(len(part) == 0 for part in parts):
        return None
    
    # Check for valid top-level domain (at least 2 characters)
    if len(parts[-1]) < 2:
        return None

    return domain


def get_domain_from_url(url_or_domain):
    """Extract and clean the domain from a URL or domain string.
    Handles malformed/invalid domains and multiple delimiters.
    """
    if not url_or_domain:
        return None
    # Remove anything before '@' so "user@domain.com" -> "domain.com"
    cleaned = url_or_domain.split('@')[-1]
    # Remove all spaces
    cleaned = cleaned.replace(' ', '')
    # If it's a URL, extract the netloc
    if '://' in cleaned:
        parsed = urlparse(cleaned)
        domain = parsed.netloc.split(':')[0] if parsed.netloc else ''
    else:
        domain = cleaned
    return clean_domain(domain)