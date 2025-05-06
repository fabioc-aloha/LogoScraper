"""Company Logo Scraper

This module provides functionality to automatically download and standardize company logos
from various sources including Clearbit API, DuckDuckGo, and fallback to generating default logos.
It coordinates the overall process flow, handling initialization, cleanup, and orchestration
of the various components.
"""

import os
import logging
import pandas as pd
import json
from datetime import datetime
from utils.progress_tracker import ProgressTracker
from utils.filter_utils import apply_filters
from utils.batch_processor import process_batch
from services.input_data_service import InputDataService
from config import CONFIG

class LogoScraper:
    """A class to manage the logo scraping and processing pipeline."""
    
    def __init__(self, output_folder=CONFIG['OUTPUT_FOLDER'], batch_size=CONFIG['BATCH_SIZE']):
        """Initialize the LogoScraper with output directory and batch size."""
        self.output_folder = output_folder
        self.temp_folder = os.path.join(os.path.dirname(output_folder), 'temp')
        self.batch_size = batch_size
        self.cache_file = os.path.join(os.path.dirname(output_folder), 'failed_domains_cache.json')
        
        # Create output and temp directories
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Initialize data collection
        self.enriched_data = []
        
        # Load failed domains cache
        self.failed_domains = self._load_failed_domains()
        
        # Initialize progress tracker
        self.total_companies = 0
        self.progress = ProgressTracker()

    def _load_failed_domains(self):
        """Load the cache of failed domains from disk."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def _save_failed_domains(self):
        """Save the cache of failed domains to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(list(self.failed_domains), f)
        except Exception as e:
            logging.error(f"Error saving failed domains cache: {str(e)}")

    def process_batch(self, df):
        """Process a batch of companies in parallel."""
        successful, total, enriched_df = process_batch(
            df=df,
            output_folder=self.output_folder,
            temp_folder=self.temp_folder,
            failed_domains=self.failed_domains,
            total_companies=self.total_companies,
            progress_tracker=self.progress
        )
        
        # Store enriched data
        self.enriched_data.append(enriched_df)
        
        return successful, total

    def save_enriched_data(self):
        """Save the enriched dataset to Excel."""
        if not self.enriched_data:
            logging.warning("No enriched data to save")
            return
            
        # Combine all batches
        final_df = pd.concat(self.enriched_data, ignore_index=True)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'Companies_Enriched_{timestamp}.xlsx'
        final_df.to_excel(output_file, index=False)
        logging.info(f"Saved enriched data to {output_file}")

    def cleanup(self):
        """Clean up resources and save final state."""
        self._save_failed_domains()
        self.save_enriched_data()

    def get_input_data(self):
        """Get input data from either Azure Storage or local Excel file."""
        try:
            # Try Azure Storage first
            input_service = InputDataService()
            df = input_service.get_data(CONFIG.get('FILTERS'), CONFIG.get('TOP_N'))
            logging.info(f"Successfully loaded {len(df):,} companies from Azure Storage")
            return df
        except Exception as e:
            logging.warning(f"Could not load from Azure Storage: {str(e)}")
            logging.info("Falling back to local Excel file...")
            
            # Fall back to local Excel file
            input_file = CONFIG['INPUT_FILE']
            logging.info(f"Reading {input_file} file...")
            df = pd.read_excel(input_file)
            
            # Apply filters and top_n limit since we couldn't use InputDataService
            df = apply_filters(df)
            if CONFIG.get('TOP_N'):
                df = df.head(CONFIG['TOP_N'])
                logging.info(f"Limited dataset to first {CONFIG['TOP_N']} records")
            
            logging.info(f"Successfully read {len(df):,} companies from {input_file}")
            return df

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
        
        # Create scraper and get input data
        scraper = LogoScraper()
        df = scraper.get_input_data()
        logging.info(f"Total companies after filtering: {len(df):,}")
        
        # Set total for progress tracking
        scraper.total_companies = len(df)
        
        # Filter out already processed TPIDs
        df['TPID'] = df['TPID'].astype(str)
        unprocessed_df = df[~df['TPID'].isin(scraper.progress.progress['completed'] + scraper.progress.progress['failed'])]
        logging.info(f"Found {len(unprocessed_df):,} unprocessed companies to process")
        
        if len(unprocessed_df) == 0:
            logging.info("No new companies to process")
            return
        
        # Process in batches
        batch_size = scraper.batch_size
        for start_idx in range(0, len(unprocessed_df), batch_size):
            end_idx = min(start_idx + batch_size, len(unprocessed_df))
            batch_df = unprocessed_df.iloc[start_idx:end_idx]
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