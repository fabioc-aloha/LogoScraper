"""URL Processing Utilities

This module provides utility functions for processing and normalizing URLs and domain names.
"""

import logging
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
    """
    if not domain:
        return None

    # Remove anything after '@'
    domain = domain.split('@')[0]

    # Split on common delimiters and use the first part
    delimiters = r'[;,/\\\s]'
    parts = re.split(delimiters, domain)
    domain = parts[0] if parts else domain

    # Remove unwanted characters
    domain = re.sub(r'["\'<>\(\)\[\]]', '', domain)

    # Remove common prefixes
    domain = domain.lower()
    if domain.startswith('www.'):
        domain = domain[4:]

    # Remove leading/trailing dots and hyphens and spaces
    domain = domain.strip(' .-')

    return domain if domain else None


def get_domain_from_url(url_or_domain):
    """Extract and clean the domain from a URL or domain string.
    Handles malformed/invalid domains and multiple delimiters.
    """
    if not url_or_domain:
        return None
    # Remove anything after '@'
    cleaned = url_or_domain.split('@')[0]
    # Remove all spaces
    cleaned = cleaned.replace(' ', '')
    # If it's a URL, extract the netloc
    if '://' in cleaned:
        parsed = urlparse(cleaned)
        domain = parsed.netloc.split(':')[0] if parsed.netloc else ''
    else:
        domain = cleaned
    return clean_domain(domain)