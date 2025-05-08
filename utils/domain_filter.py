"""Domain Filtering Module

This module handles domain filtering and validation.
"""

import re

class DomainFilter:
    """Handles domain filtering logic."""

    def __init__(self, excluded_domains=None):
        """Initialize the domain filter.
        
        Args:
            excluded_domains: List of domain patterns to exclude
        """
        self.excluded_domains = excluded_domains or [
            'linkedin.com',
            'facebook.com',
            'twitter.com',
            'wikipedia.org',
            'bloomberg.com',
            'reuters.com',
            'youtube.com',
            'instagram.com'
        ]
        
        # Known domain patterns for common institutions
        self.domain_patterns = {
            # Universities (with variants)
            r'university of (.+)': lambda x: f"{x.replace(' ', '').lower()}.edu",
            r'(.+) university': lambda x: f"{x.replace(' ', '').lower()}.edu",
            # Common university abbreviations
            'princeton university': 'princeton.edu',
            'george washington university': 'gwu.edu',
            'university of iowa': 'uiowa.edu',
            'university of rochester': 'rochester.edu',
            'university of north carolina system': 'northcarolina.edu',
            'university of colorado system': 'cu.edu',
            
            # Major corporations
            'lockheed martin corporation': 'lockheedmartin.com',
            'conagra foods': 'conagrafoods.com',
            'nrg energy': 'nrg.com',
            'hexagon': 'hexagon.com'
        }

    def get_known_domain(self, company_name):
        """Try to match company name to a known domain pattern."""
        if not company_name:
            return None
            
        company_name = company_name.lower().strip()
        
        # Check exact matches first
        if company_name in self.domain_patterns:
            pattern = self.domain_patterns[company_name]
            if isinstance(pattern, str):
                return pattern
            elif callable(pattern):
                return pattern(company_name)
            
        # Try regex patterns
        for pattern, domain_func in self.domain_patterns.items():
            if isinstance(pattern, str):
                continue
            match = re.match(pattern, company_name, re.IGNORECASE)
            if match:
                try:
                    captured = match.group(1).strip()
                    return domain_func(captured)
                except:
                    continue
        return None

    def is_excluded(self, domain):
        """Check if a domain matches any exclusion patterns."""
        if not domain:
            return True
        return any(x in domain.lower() for x in self.excluded_domains)

    def is_valid(self, domain):
        """Check if a domain is valid for use."""
        if not domain:
            return False
        if len(domain.strip()) < 4:  # Minimum reasonable domain length
            return False
        if not re.match(r'^[a-zA-Z0-9]', domain):  # Must start with alphanumeric
            return False
        if not '.' in domain:  # Must have at least one dot
            return False
        return not self.is_excluded(domain)