"""Company Processing Module

This module orchestrates the logo acquisition process for individual companies
using specialized modules for URL discovery, logo retrieval, and image processing.

Classes:
- CompanyProcessor: Handles the end-to-end process of obtaining, saving, and enriching a logo for a single company, including fallbacks and error handling.

This module is called by the batch processor and is central to the logo scraping workflow.
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
                favicon_data, favicon_provider, favicon_size = self.favicon_service.get_logo(domain)
                if favicon_data:
                    output_path = os.path.join(self.output_folder, f"{tpid}.png")
                    enrichment_data = {
                        'DiscoveredURL': None,
                        'FinalDomain': domain,
                        'LogoSource': favicon_provider if favicon_provider else 'Favicon',
                        'LogoSize': favicon_size if favicon_size else None,
                        'URLSource': 'Favicon Service',
                        'OutputPath': output_path
                    }
                    success = self._save_logo(favicon_data, tpid, company_name)
                    if success:
                        logging.info(f"[TPID {tpid}] SUCCESS: Logo for '{company_name}' fetched via Favicon service ({favicon_provider})")
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

from utils.url_utils import get_domain_from_url
from utils.image_resizer import save_standardized_logo, ImageProcessingError
from config import CONFIG

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
            return self._fail_result("Missing Company Name", tpid)
        
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
                        'TPID': tpid, # Ensure TPID is in enrichment data
                        'DiscoveredURL': None,
                        'FinalDomain': domain,
                        'LogoSource': "Clearbit",
                        'URLSource': 'Primary URL',
                        'OutputPath': output_path,
                        'ErrorMessage': None # Initialize error message field
                    }
                    success = self._save_logo(logo_data, tpid, company_name, enrichment_data)
                    if success:
                        logging.info(f"[TPID {tpid}] SUCCESS: Logo for '{company_name}' fetched via Clearbit API")
                        return True, enrichment_data['LogoSource'], enrichment_data
                    else: # _save_logo failed, enrichment_data is updated by it
                        logging.warning(f"[TPID {tpid}] Clearbit logo saving failed for '{company_name}': {enrichment_data.get('ErrorMessage')}")
                        # Fall through to Favicon if Clearbit saving failed
                
                logging.info(f"[TPID {tpid}] Trying favicon service for domain: {domain}")
                favicon_data, favicon_provider, favicon_size = self.favicon_service.get_logo(domain)
                if favicon_data:
                    output_path = os.path.join(self.output_folder, f"{tpid}.png")
                    enrichment_data = {
                        'TPID': tpid,
                        'DiscoveredURL': None, # Or the URL used by favicon service if available
                        'FinalDomain': domain,
                        'LogoSource': favicon_provider if favicon_provider else 'Favicon',
                        'LogoSize': favicon_size if favicon_size else None,
                        'URLSource': 'Favicon Service',
                        'OutputPath': output_path,
                        'ErrorMessage': None
                    }
                    success = self._save_logo(favicon_data, tpid, company_name, enrichment_data)
                    if success:
                        logging.info(f"[TPID {tpid}] SUCCESS: Logo for '{company_name}' fetched via Favicon service ({favicon_provider})")
                        return True, enrichment_data['LogoSource'], enrichment_data
                    else: # _save_logo failed
                        logging.warning(f"[TPID {tpid}] Favicon logo saving failed for '{company_name}': {enrichment_data.get('ErrorMessage')}")
                        # Fall through to Default if Favicon saving failed
            else:
                logging.info(f"[TPID {tpid}] Could not extract domain from URL: {primary_url}")
        else:
            logging.info(f"[TPID {tpid}] No website URL available for '{company_name}'")

        # Default logo as fallback
        source = "Default"
        logging.info(f"[TPID {tpid}] Generating default logo for '{company_name}'")
        logo_data = self.default_service.get_logo(company_name)
        
        if not logo_data: # Should not happen with current DefaultService, but good practice
            logging.error(f"[TPID {tpid}] FAILED: Could not generate default logo for '{company_name}'")
            return self._fail_result("Default Logo Generation Failed", tpid)
            
        output_path = os.path.join(self.output_folder, f"{tpid}.png")
        enrichment_data = {
            'TPID': tpid,
            'DiscoveredURL': None,
            'FinalDomain': None,
            'LogoSource': source,
            'URLSource': 'Default Generation',
            'OutputPath': output_path,
            'ErrorMessage': None
        }
        success = self._save_logo(logo_data, tpid, company_name, enrichment_data)
        if success:
            logging.info(f"[TPID {tpid}] SUCCESS: Default logo generated and saved for '{company_name}'")
            return True, source, enrichment_data
            
        # If default logo saving failed
        logging.error(f"[TPID {tpid}] FAILED: Could not save default logo for '{company_name}'. Reason: {enrichment_data.get('ErrorMessage')}")
        return False, f"Failed (Default Save Error: {enrichment_data.get('ErrorMessage', 'Unknown')})", enrichment_data


    def _save_logo(self, logo_data: bytes, tpid: str, company_name: str, enrichment_data: Dict) -> bool:
        """
        Save a logo to disk with standardization, handling ImageProcessingError.
        Updates enrichment_data with error message if saving fails.
        """
        output_path = os.path.join(self.output_folder, f"{tpid}.png")
        enrichment_data['OutputPath'] = output_path # Ensure output path is in enrichment data

        try:
            save_standardized_logo(logo_data, output_path)
            logging.info(f"[TPID {tpid}] Logo for '{company_name}' saved successfully to {output_path} (Source: {enrichment_data.get('LogoSource', 'Unknown')})")
            enrichment_data['ErrorMessage'] = None # Explicitly set no error
            return True
        except ImageProcessingError as e:
            # Log the specific error from image_resizer
            error_message = f"Image processing/saving error for '{company_name}' (TPID {tpid}): {e}"
            logging.error(error_message)
            enrichment_data['ErrorMessage'] = str(e) # Store the error message
            # Attempt to remove partially saved file if an error occurred
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logging.debug(f"Removed partially saved or problematic file: {output_path}")
                except OSError as rm_error:
                    logging.error(f"Could not remove problematic file {output_path}: {rm_error}")
            return False
        except Exception as e: # Catch any other unexpected errors during save
            error_message = f"Unexpected error saving logo for '{company_name}' (TPID {tpid}): {str(e)}"
            logging.error(error_message)
            enrichment_data['ErrorMessage'] = str(e)
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError as rm_error:
                    logging.error(f"Could not remove problematic file {output_path} post-unexpected-error: {rm_error}")
            return False

    def _fail_result(self, reason: str, tpid: str, enrichment_data: Dict = None) -> Tuple[bool, str, Dict]:
        """Create a standardized failure result, ensuring TPID and error message are included."""
        final_reason = f"Failed ({reason})"
        if enrichment_data:
            enrichment_data['LogoSource'] = final_reason
            enrichment_data['TPID'] = tpid # Ensure TPID is present
            if 'ErrorMessage' not in enrichment_data or not enrichment_data['ErrorMessage']:
                 enrichment_data['ErrorMessage'] = reason # Populate error message if not already specific
        else: # Create enrichment_data if it's None
            enrichment_data = {
                'TPID': tpid,
                'DiscoveredURL': None,
                'FinalDomain': None,
                'LogoSource': final_reason,
                'URLSource': None,
                'OutputPath': None,
                'ErrorMessage': reason
            }
        return False, final_reason, enrichment_data

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'clearbit_service'):
            self.clearbit_service.close()
        if hasattr(self, 'favicon_service'):
            self.favicon_service.close()