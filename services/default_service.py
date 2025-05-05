"""Default Logo Generation Service

This module provides functionality to generate default logos for companies when
no suitable logo can be found from online sources. It creates visually appealing
logos using company initials or names, with consistent styling and professional
color schemes.

The service supports multiple languages and provides fallback mechanisms for
font loading and text rendering.
"""

import os
import sys
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.image_utils import create_default_logo

class DefaultService:
    """Service class for generating default company logos.
    
    This class handles the creation of default logos when no suitable logo can
    be found from online sources. It generates visually appealing logos using
    company names or initials with consistent styling.
    
    Args:
        target_size (int): The desired size of the logo in pixels.
            The generated logo will match this size exactly.
    
    Attributes:
        target_size (int): The size of the generated logo in pixels
    """

    def __init__(self, target_size):
        """Initialize the default logo service with the target logo size."""
        self.target_size = target_size  # Keep for consistency with other services

    def get_logo(self, company_name):
        """Create a default logo using the company name.
        
        This method generates a logo by rendering the company name or initials
        in a professional style with consistent branding elements.
        
        Args:
            company_name (str): The name of the company to use for the logo.
        
        Returns:
            bytes or None: The generated logo as PNG image data if successful,
                None if the logo could not be generated or the company name
                is invalid.
        
        The generated logo features:
        - Professional color schemes
        - Rounded corners
        - Properly centered text
        - Support for long company names
        - Fallback to initials for very long names
        - Multi-language text support
        """
        if not company_name:
            return None
        try:
            logo_data = create_default_logo(company_name)
            if logo_data:
                return logo_data
        except Exception as e:
            logging.error(f"Error creating default logo for {company_name}: {str(e)}")
        return None