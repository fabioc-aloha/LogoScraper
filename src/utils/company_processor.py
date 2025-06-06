"""Company Processing Module

This module orchestrates the logo acquisition process for individual companies
using specialized modules for URL discovery, logo retrieval, and image processing.
"""

import logging
import os
from typing import Optional, Tuple, Dict

from src.services.clearbit_service import ClearbitService
from src.services.favicon_service import FaviconService
from src.services.default_service import DefaultService
from src.utils.url_utils import get_domain_from_url
from src.utils.image_resizer import save_standardized_logo
from src.config import CONFIG

class CompanyProcessor:
    """Orchestrates company logo processing."""
    
    def __init__(self, output_folder: str, temp_folder: str):
        """Initialize the company processor."""
        self.output_folder = output_folder
        self.temp_folder = temp_folder
        self.target_size = CONFIG['OUTPUT_SIZE']
        
        # Initialize core services
        self.clearbit_service = ClearbitService(self.target_size)
        self.favicon_service = FaviconService(self.target_size)
        self.default_service = DefaultService(self.target_size)

    def process_company(self, row) -> Tuple[bool, str, Dict]:
        """Process a single company to obtain and save its logo."""
        tpid = str(row['tpid'])
        company_name = row.get('crmaccountname', '').strip()
        
        if not company_name:
            logging.warning(f"No company name for TPID {tpid}")
            return self._fail_result("Missing Company Name")
        
        logging.info(f"Processing company: {company_name} (TPID: {tpid})")
            
        # Try to get logo using URL from input
        primary_url = row.get('websiteurl', '').strip()
        if primary_url:
            domain = get_domain_from_url(primary_url)
            if domain:
                logging.info(f"[TPID {tpid}] Trying Clearbit API for domain: {domain}")
                logo_data = self.clearbit_service.get_logo(domain)
                if logo_data:
                    output_path = os.path.join(self.output_folder, f"{tpid}.png")
                    enrichment_data = {
                        'DiscoveredURL': None,
                        'FinalDomain': domain,
                        'LogoSource': "Clearbit",
                        'URLSource': 'Primary URL',
                        'OutputPath': output_path
                    }
                    success = self._save_logo(logo_data, tpid, company_name)
                    if success:
                        logging.info(f"[TPID {tpid}] SUCCESS: Logo for '{company_name}' fetched via Clearbit API")
                        return True, enrichment_data['LogoSource'], enrichment_data
                else:
                    logging.info(f"[TPID {tpid}] Clearbit API failed for '{company_name}' with domain {domain}")
                
                # Fallback to favicon service
                logging.info(f"[TPID {tpid}] Trying favicon service for domain: {domain}")
                favicon_data = self.favicon_service.get_logo(domain)
                if favicon_data:
                    output_path = os.path.join(self.output_folder, f"{tpid}.png")
                    enrichment_data = {
                        'DiscoveredURL': None,
                        'FinalDomain': domain,
                        'LogoSource': 'Favicon',
                        'URLSource': 'Favicon Service',
                        'OutputPath': output_path
                    }
                    success = self._save_logo(favicon_data, tpid, company_name)
                    if success:
                        logging.info(f"[TPID {tpid}] SUCCESS: Logo for '{company_name}' fetched via Favicon service")
                        return True, enrichment_data['LogoSource'], enrichment_data
                else:
                    logging.info(f"[TPID {tpid}] Favicon service failed for '{company_name}' with domain {domain}")
            else:
                logging.info(f"[TPID {tpid}] Could not extract domain from URL: {primary_url}")
        else:
            logging.info(f"[TPID {tpid}] No website URL available for '{company_name}'")

        # Default logo as fallback
        source = "Default"
        logging.info(f"[TPID {tpid}] Generating default logo for '{company_name}'")
        logo_data = self.default_service.get_logo(company_name)
        
        if not logo_data:
            logging.error(f"[TPID {tpid}] FAILED: Could not generate default logo for '{company_name}'")
            return self._fail_result("Default Logo Generation Failed")
            
        output_path = os.path.join(self.output_folder, f"{tpid}.png")
        success = self._save_logo(logo_data, tpid, company_name)
        if success:
            logging.info(f"[TPID {tpid}] SUCCESS: Default logo generated for '{company_name}'")
            enrichment_data = {
                'DiscoveredURL': None,
                'FinalDomain': None,
                'LogoSource': source,
                'URLSource': None,
                'OutputPath': output_path
            }
            return True, source, enrichment_data
            
        logging.error(f"[TPID {tpid}] FAILED: Could not save default logo for '{company_name}'")
        return self._fail_result("Storage Error")

    def _save_logo(self, logo_data: bytes, tpid: str, company_name: str = "") -> bool:
        """Save a logo to disk with standardization."""
        try:
            output_path = os.path.join(self.output_folder, f"{tpid}.png")
            result = save_standardized_logo(logo_data, output_path)
            if result:
                logging.info(f"[TPID {tpid}] Logo saved successfully to {output_path}")
            return result
        except Exception as e:
            logging.error(f"[TPID {tpid}] Error saving logo for '{company_name}': {str(e)}")
            return False

    def _fail_result(self, reason: str, enrichment_data: Dict = None) -> Tuple[bool, str, Dict]:
        """Create a standardized failure result."""
        if enrichment_data is None:
            enrichment_data = {
                'DiscoveredURL': None,
                'FinalDomain': None,
                'LogoSource': f"Failed ({reason})",
                'URLSource': None
            }
        else:
            enrichment_data['LogoSource'] = f"Failed ({reason})"
        return False, f"Failed ({reason})", enrichment_data

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'clearbit_service'):
            self.clearbit_service.close()
        if hasattr(self, 'favicon_service'):
            self.favicon_service.close()