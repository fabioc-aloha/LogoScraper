"""Company Logo Scraper

This module provides functionality to automatically download and standardize company logos
from various sources including Clearbit API, DuckDuckGo, and fallback to generating default logos.
It supports parallel processing, resource management, and progress tracking.

The script processes companies in batches, with configurable settings for batch size,
output dimensions, and API rate limits. It includes comprehensive error handling and
cleanup of temporary resources.

Example:
    >>> scraper = LogoScraper()
    >>> scraper.total_companies = len(df)
    >>> successful, total = scraper.process_batch(batch_df)
"""

import os
import logging
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
import json
from services.clearbit_service import ClearbitService
from services.duckduckgo_service import DuckDuckGoService
from services.default_service import DefaultService
from utils.url_utils import clean_url, get_domain_from_url
from utils.image_utils import save_standardized_logo
from utils.progress_tracker import ProgressTracker
from config import CONFIG

class LogoScraper:
    """A class to manage the logo scraping and processing pipeline.
    
    This class handles the entire workflow of downloading, processing, and saving
    company logos. It supports parallel processing, maintains a cache of failed
    domains, and provides progress tracking.

    Args:
        output_folder (str): Directory where processed logos will be saved.
            Defaults to CONFIG['OUTPUT_FOLDER'].
        batch_size (int): Number of companies to process in each batch.
            Defaults to CONFIG['BATCH_SIZE'].

    Attributes:
        output_folder (str): Directory where processed logos are saved
        temp_folder (str): Directory for temporary files during processing
        batch_size (int): Size of each processing batch
        cache_file (str): Path to the failed domains cache file
        failed_domains (set): Set of domains that previously failed
        total_companies (int): Total number of companies to process
        progress (ProgressTracker): Tracks processing progress
    """

    def __init__(self, output_folder=CONFIG['OUTPUT_FOLDER'], batch_size=CONFIG['BATCH_SIZE']):
        """Initialize the LogoScraper with output directory and batch size."""
        self.output_folder = output_folder
        self.temp_folder = os.path.join(os.path.dirname(output_folder), 'temp')
        self.batch_size = batch_size
        self.cache_file = os.path.join(os.path.dirname(output_folder), 'failed_domains_cache.json')
        
        # Create output and temp directories
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Load failed domains cache
        self.failed_domains = self._load_failed_domains()
        
        # Initialize progress tracker
        self.total_companies = 0
        self.progress = ProgressTracker()

    def cleanup(self):
        """Clean up all temporary resources and save cache state.
        
        This method ensures proper cleanup of:
        - Temporary files and directories
        - Failed domains cache
        - Any other resources that need to be released

        The method is designed to be safe to call multiple times and handles
        its own exceptions to ensure maximum cleanup even in error cases.
        """
        try:
            # Clean up temp folder
            if os.path.exists(self.temp_folder):
                for file in os.listdir(self.temp_folder):
                    try:
                        os.remove(os.path.join(self.temp_folder, file))
                    except:
                        pass
                try:
                    os.rmdir(self.temp_folder)
                except:
                    pass
            # Save any remaining failed domains
            self._save_failed_domains()
        except:
            pass

    def __del__(self):
        """Ensure cleanup when the object is destroyed."""
        self.cleanup()

    def _load_failed_domains(self):
        """Load the set of failed domains from cache file.
        
        Returns:
            set: A set of domain names that previously failed to provide valid logos.
                Returns an empty set if the cache file doesn't exist or is invalid.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _save_failed_domains(self):
        """Save the current set of failed domains to the cache file.
        
        This method safely serializes the failed_domains set to JSON format
        and saves it to the cache file. Any errors during saving are caught
        and logged to prevent disrupting the main process.
        """
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(list(self.failed_domains), f)
        except:
            pass

    @staticmethod
    def process_company_static(row_data, output_folder, temp_folder, failed_domains):
        """Process a single company's logo in a worker process.
        
        This static method is designed to run in a separate process and handles
        the complete workflow for a single company: fetching the logo from
        various sources, validating it, and saving the result.

        Args:
            row_data (tuple): Tuple of (pandas.Series, str) containing the company
                data row and TPID.
            output_folder (str): Directory where the final logo should be saved.
            temp_folder (str): Directory for temporary files during processing.
            failed_domains (set): Set of domains that have previously failed.

        Returns:
            tuple: (bool, str, str) containing:
                - Success status (True/False)
                - TPID of the processed company
                - Source of the logo ("Clearbit", "DuckDuckGo", "Default", or None)

        The method ensures proper cleanup of resources even in case of errors,
        including:
        - Closing service connections
        - Removing temporary files
        - Releasing memory resources
        """
        # Initialize services
        clearbit = None
        duckduckgo = None
        default = None
        temp_path = None
        
        try:
            clearbit = ClearbitService(CONFIG['OUTPUT_SIZE'])
            duckduckgo = DuckDuckGoService(CONFIG['OUTPUT_SIZE'])
            default = DefaultService(CONFIG['OUTPUT_SIZE'])
            
            row, tpid = row_data
            
            # Get company details
            company_name = None
            if pd.notna(row['TPAccountName']):
                company_name = str(row['TPAccountName'])
            elif pd.notna(row['CRMAccountName']):
                company_name = str(row['CRMAccountName'])

            urls = [
                str(row['WebsiteURL']) if pd.notna(row['WebsiteURL']) else None,
                str(row['WebsiteURLspm']) if pd.notna(row['WebsiteURLspm']) else None
            ]

            logo_data = None
            logo_source = None
            
            # Try each URL with both services
            for url in urls:
                if not url:
                    continue
                    
                website = clean_url(url)
                if not website:
                    continue
                    
                domain = get_domain_from_url(website)
                if not domain or domain in failed_domains:
                    continue
                
                # Try Clearbit first
                temp_data = clearbit.get_logo(domain)
                if temp_data:
                    # Try to save and validate the logo
                    temp_path = os.path.join(temp_folder, f"{tpid}_clearbit.png")
                    if save_standardized_logo(temp_data, temp_path):
                        logo_data = temp_data
                        logo_source = "Clearbit"
                        os.remove(temp_path)
                        break
                    elif os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                # Try DuckDuckGo if Clearbit failed
                if not logo_data:
                    temp_data = duckduckgo.get_logo(domain)
                    if temp_data:
                        temp_path = os.path.join(temp_folder, f"{tpid}_duckduckgo.png")
                        if save_standardized_logo(temp_data, temp_path):
                            logo_data = temp_data
                            logo_source = "DuckDuckGo"
                            os.remove(temp_path)
                            break
                        elif os.path.exists(temp_path):
                            os.remove(temp_path)
                
                if not logo_data:
                    failed_domains.add(domain)

            # Create default logo if no valid logo found
            if not logo_data and company_name:
                logo_data = default.get_logo(company_name)
                logo_source = "Default"

            # Save final logo if found
            if logo_data:
                output_path = os.path.join(output_folder, f"{tpid}.png")
                if save_standardized_logo(logo_data, output_path):
                    return True, tpid, logo_source

            return False, tpid, None
            
        finally:
            # Cleanup services
            for service in [clearbit, duckduckgo, default]:
                if service and hasattr(service, 'close'):
                    try:
                        service.close()
                    except:
                        pass
            
            # Cleanup any remaining temporary files
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def process_batch(self, df):
        """Process a batch of companies in parallel.
        
        This method distributes the companies across multiple processes for
        parallel processing, tracks progress, and provides regular status updates.

        Args:
            df (pandas.DataFrame): DataFrame containing the batch of companies
                to process. Must contain required columns (TPID, TPAccountName,
                CRMAccountName, WebsiteURL, WebsiteURLspm).

        Returns:
            tuple: (int, int) containing:
                - Number of successfully processed companies
                - Total number of companies attempted

        This method handles:
        - Creating and managing the process pool
        - Distributing work across processes
        - Progress tracking and logging
        - Cache updates
        - Resource cleanup
        """
        total = len(df)
        completed = 0
        successful = 0
        
        # Prepare data for parallel processing
        row_data = [(row, str(row['TPID'])) for _, row in df.iterrows()]
        
        # Use number of CPUs minus 1 to leave one core free
        num_processes = max(1, cpu_count() - 1)
        
        # Create partial function with fixed arguments
        process_func = partial(
            self.process_company_static,
            output_folder=self.output_folder,
            temp_folder=self.temp_folder,
            failed_domains=self.failed_domains
        )
        
        # Process companies in parallel
        with Pool(num_processes) as pool:
            for success, tpid, source in pool.imap_unordered(process_func, row_data):
                completed += 1
                if success:
                    successful += 1
                    self.progress.mark_completed(tpid)
                    logging.info(f"Successfully saved logo for TPID {tpid} from {source}")
                else:
                    self.progress.mark_failed(tpid)
                    logging.error(f"Failed to process logo for TPID {tpid}")
                
                if completed % 10 == 0:
                    success_rate = (successful / completed) * 100
                    total_completed = len(self.progress.progress['completed'])
                    total_failed = len(self.progress.progress['failed'])
                    total_processed = total_completed + total_failed
                    overall_progress = (total_processed / self.total_companies * 100)
                    
                    logging.info(
                        f"Batch Progress: {completed}/{total} ({completed/total:.1%}). Success rate: {success_rate:.1f}%\n"
                        f"Overall Progress: {total_processed}/{self.total_companies} TPIDs processed ({overall_progress:.1f}%). "
                        f"Successful: {total_completed}, Failed: {total_failed}"
                    )
        
        # Save updated failed domains cache
        self._save_failed_domains()
        return successful, completed

def main():
    scraper = None
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logo_scraper.log'),
                logging.StreamHandler()
            ]
        )
        
        # Read Excel file
        input_file = CONFIG['INPUT_FILE']
        logging.info(f"Reading {input_file} file...")
        df = pd.read_excel(input_file)
        logging.info(f"Successfully read {len(df):,} companies from {input_file}")
        
        # Create scraper
        scraper = LogoScraper()
        scraper.total_companies = len(df)
        
        # Process in batches
        batch_size = scraper.batch_size
        for start_idx in range(0, len(df), batch_size):
            end_idx = min(start_idx + batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            successful, total = scraper.process_batch(batch_df)
            logging.info(f"Batch complete: {successful}/{total} successful")
            
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()