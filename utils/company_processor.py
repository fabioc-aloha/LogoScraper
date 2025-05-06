"""Company Processing Module

This module handles the processing of individual companies, including URL discovery,
logo retrieval, and fallback mechanisms.
"""

import logging
import os
from typing import Optional, Tuple, Dict

from services.clearbit_service import ClearbitService
from services.default_service import DefaultService
from services.company_search_service import CompanySearchService
from services.azure_storage_service import AzureStorageService
from services.azure_vision_service import AzureVisionService
from utils.url_utils import get_domain_from_url, clean_url
from config import CONFIG

class CompanyProcessor:
    """Processes individual companies to obtain their logos.
    
    This class coordinates the various services needed to process a company,
    including URL discovery, logo retrieval, and fallback mechanisms.
    """
    
    def __init__(self, output_folder: str, temp_folder: str):
        """Initialize the company processor.
        
        Args:
            output_folder: Directory where processed logos will be saved
            temp_folder: Directory for temporary files during processing
        """
        self.output_folder = output_folder
        self.temp_folder = temp_folder
        self.target_size = CONFIG['OUTPUT_SIZE']
        
        # Initialize services
        self.clearbit_service = ClearbitService(self.target_size)
        self.default_service = DefaultService(self.target_size)
        self.company_search = CompanySearchService()
        
        # Initialize Azure services
        try:
            self.azure_storage = AzureStorageService()
            self.azure_vision = AzureVisionService()
            self.use_azure = True
        except Exception as e:
            logging.warning(f"Failed to initialize Azure services: {str(e)}")
            self.use_azure = False

    def discover_url(self, company_name: str, country: Optional[str] = None) -> Optional[str]:
        """Try to discover a company's URL if none is provided.
        
        Args:
            company_name: Name of the company
            country: Optional country for better targeting
            
        Returns:
            Discovered URL or None if no URL could be found
        """
        try:
            return self.company_search.discover_url(company_name, country)
        except Exception as e:
            logging.error(f"Error discovering URL for {company_name}: {str(e)}")
            return None

    def process_company(self, row) -> Tuple[bool, str, Dict]:
        """Process a single company to obtain and save its logo.
        
        Args:
            row: DataFrame row containing company information
            
        Returns:
            Tuple containing:
            - Success status (bool)
            - Source of the logo ("Clearbit", "Default (No URLs)", etc.)
            - Dictionary with enrichment data including discovered URL and domain
        """
        tpid = str(row['TPID'])
        company_name = row['TPAccountName']
        primary_url = clean_url(row.get('WebsiteURL'))
        backup_url = clean_url(row.get('WebsiteURLspm'))
        country = row.get('Country')
        
        enrichment_data = {
            'DiscoveredURL': None,
            'FinalDomain': None,
            'LogoSource': None,
            'URLSource': None,
            'LogoQualityScore': None,
            'LogoURL': None
        }
        
        # Get domain from URLs or discover URL if none provided
        domain = None
        url_source = None
        final_url = None
        
        if primary_url:
            domain = get_domain_from_url(primary_url)
            url_source = "Primary URL"
            final_url = primary_url
        
        if not domain and backup_url:
            domain = get_domain_from_url(backup_url)
            url_source = "Backup URL"
            final_url = backup_url
            
        if not domain:
            discovered_url = self.discover_url(company_name, country)
            if discovered_url:
                domain = get_domain_from_url(discovered_url)
                url_source = "Discovered URL"
                final_url = discovered_url
                enrichment_data['DiscoveredURL'] = discovered_url
                logging.info(f"Discovered URL for {company_name}: {discovered_url}")
        
        enrichment_data['FinalDomain'] = domain
        enrichment_data['URLSource'] = url_source
        
        logo_data = None
        source = None
        
        if domain:
            # Try Clearbit first
            logo_data = self.clearbit_service.get_logo(domain)
            if logo_data:
                source = f"Clearbit ({url_source})"
        
        # Fall back to default logo if needed
        if not logo_data:
            reason = "No URLs" if not url_source else "No Logo Found"
            source = f"Default ({reason})"
            logo_data = self.default_service.get_logo(company_name)
        
        if not logo_data:
            enrichment_data['LogoSource'] = f"Failed ({reason})"
            return False, f"Failed ({reason})", enrichment_data
            
        # Validate and analyze logo with Azure Computer Vision if available
        if self.use_azure and self.azure_vision:
            try:
                is_valid, reason = self.azure_vision.validate_logo(logo_data)
                if not is_valid:
                    logging.warning(f"Logo validation failed for {tpid}: {reason}")
                    # Still continue with the logo, but log the issue
                
                analysis = self.azure_vision.analyze_logo(logo_data)
                if analysis:
                    enrichment_data['LogoQualityScore'] = analysis['quality_score']
            except Exception as e:
                logging.error(f"Error validating logo with Azure Vision: {str(e)}")
        
        # Save logo
        if self.use_azure and self.azure_storage:
            try:
                # Save to Azure Storage with CDN
                cdn_url = self.azure_storage.save_logo(tpid, logo_data)
                if cdn_url:
                    enrichment_data['LogoURL'] = cdn_url
                    enrichment_data['LogoSource'] = source
                    return True, source, enrichment_data
            except Exception as e:
                logging.error(f"Error saving to Azure Storage: {str(e)}")
                # Fall back to local storage
        
        # Fall back to local storage if Azure is not available
        try:
            output_path = os.path.join(self.output_folder, f"{tpid}.png")
            with open(output_path, 'wb') as f:
                f.write(logo_data)
            enrichment_data['LogoSource'] = source
            return True, source, enrichment_data
        except Exception as e:
            logging.error(f"Error saving logo locally: {str(e)}")
            enrichment_data['LogoSource'] = f"Failed (Storage Error)"
            return False, "Failed (Storage Error)", enrichment_data

    def cleanup(self):
        """Clean up resources used by the processor."""
        if hasattr(self, 'clearbit_service'):
            self.clearbit_service.close()