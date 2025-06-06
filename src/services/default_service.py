"""Default Logo Generation Service

This module provides functionality to generate default logos when no suitable logo
can be found online. It is the final fallback in the logo scraping pipeline.

Classes:
- DefaultService: Generates a default logo image using the company name.

This ensures every company can have a logo, even if no online image is available.
"""

import logging
from src.utils.default_logo_generator import create_default_logo

class DefaultService:
    """Service class for generating default company logos."""

    def __init__(self, target_size):
        """Initialize the default logo service."""
        self.target_size = target_size

    def get_logo(self, company_name):
        """Create a default logo using the company name."""
        if not company_name:
            return None
        try:
            return create_default_logo(company_name)
        except Exception as e:
            logging.error(f"Error creating default logo for {company_name}: {str(e)}")
        return None