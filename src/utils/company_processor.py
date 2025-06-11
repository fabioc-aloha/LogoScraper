"""Company Processing Module

This module handles the logo acquisition process for individual companies."""

import os
from typing import Tuple

from src.services.clearbit_service import ClearbitService
from src.services.favicon_service import FaviconService
from src.services.default_service import DefaultService
from src.utils.url_utils import get_domain_from_url
from src.utils.image_resizer import save_standardized_logo
from src.config import CONFIG

class CompanyProcessor:
    """Handles the logo acquisition process for a single company."""
    
    def __init__(self, output_folder: str):
        """Initialize the company processor with basic services."""
        self.output_folder = output_folder
        # Ensure output directory exists
        os.makedirs(output_folder, exist_ok=True)
        
        self.target_size = CONFIG['OUTPUT_SIZE']
        
        # Initialize core services
        self.clearbit_service = ClearbitService(self.target_size)
        self.favicon_service = FaviconService(self.target_size)
        self.default_service = DefaultService(self.target_size)

    def process_company(self, row) -> Tuple[bool, str]:
        """Process a single company to obtain and save its logo.
        
        Returns:
            Tuple[bool, str]: (success, source) where source is one of 'Clearbit', 'Favicon', or 'Default'
        """
        id = str(row['ID'])
        company_name = row.get('CompanyName', '').strip()
        
        if not company_name:
            return False, "Missing Company Name"
        
        # Try to get logo using URL from input
        primary_url = row.get('WebsiteURL', '').strip()
        if primary_url:
            domain = get_domain_from_url(primary_url)
            if domain:
                # Try Clearbit first
                logo_data = self.clearbit_service.get_logo(domain)
                if logo_data:
                    if self._save_logo(logo_data, id):
                        return True, "Clearbit"
                
                # Fallback to favicon service
                favicon_data, favicon_provider, _ = self.favicon_service.get_logo(domain)
                if favicon_data:
                    if self._save_logo(favicon_data, id):
                        return True, favicon_provider or "Favicon"

        # Default logo as fallback
        logo_data = self.default_service.get_logo(company_name)
        if logo_data and self._save_logo(logo_data, id):
            return True, "Default"
            
        return False, "Failed"

    def _save_logo(self, logo_data: bytes, id: str) -> bool:
        """Save a logo to disk with standardization."""
        output_path = os.path.join(self.output_folder, f"{id}.png")
        try:
            save_standardized_logo(logo_data, output_path)
            return True
        except Exception:
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            return False

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'clearbit_service'):
            self.clearbit_service.close()
        if hasattr(self, 'favicon_service'):
            self.favicon_service.close()