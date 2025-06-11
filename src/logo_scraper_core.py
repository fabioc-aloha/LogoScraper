"""Core Logo Scraper Module

This module manages the company logo scraping and processing pipeline."""

import os
import sys
import time
import logging
import pandas as pd
from src.utils.batch_processor import process_batch
from src.services.input_data_service import InputDataService
from src.utils.config_validator import ConfigValidator
from src.config import CONFIG

class LogoScraper:
    """Manages the company logo scraping and processing pipeline."""
    
    def __init__(self, output_folder: str = CONFIG['OUTPUT_FOLDER'], batch_size: int = CONFIG['BATCH_SIZE']):
        self.start_time = time.time()
        self.output_folder = output_folder
        self.batch_size = batch_size
        
        # Create base data directory if it doesn't exist
        if not os.path.exists(CONFIG['BASE_DATA_DIR']):
            os.makedirs(CONFIG['BASE_DATA_DIR'], exist_ok=True)
            logging.info(f"Created base data directory: {CONFIG['BASE_DATA_DIR']}")

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"Ensured output directory exists: {output_folder}")

        # Setup temp folder under BASE_DATA_DIR if not specified elsewhere
        temp_folder = CONFIG['TEMP_FOLDER']
        os.makedirs(temp_folder, exist_ok=True)
        logging.info(f"Ensured temp directory exists: {temp_folder}")
          # Validate configuration
        validator = ConfigValidator(CONFIG)
        if not validator.validate():
            sys.exit(1)
            
        self.total_companies = 0
        self.total_successful = 0
        self.total_failed = 0
        self.results = []  # Store basic processing results

    def get_input_data(self) -> pd.DataFrame:
        """Get input data from the configured source."""
        input_service = InputDataService()
        df = input_service.get_data(
            filters=CONFIG.get('filters'),
            top_n=CONFIG.get('TOP_N')
        )
          # Filter to specific IDs if specified
        if 'id_filter' in CONFIG and CONFIG['id_filter']:
            ids = CONFIG['id_filter']
            df = df[df['ID'].astype(str).isin(ids)]
            if len(df) == 0:
                sys.exit(1)
        
        return df

    def filter_existing_logos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out companies that already have logos in the output folder.
        
        Args:
            df: Input DataFrame with company data
            
        Returns:
            DataFrame with existing logos filtered out
        """
        if df.empty:
            return df
            
        initial_count = len(df)
        existing_ids = []
        
        # Check which IDs already have logo files
        for _, row in df.iterrows():
            logo_path = os.path.join(self.output_folder, f"{row['ID']}.png")
            if os.path.exists(logo_path):
                existing_ids.append(str(row['ID']))
        
        if existing_ids:
            # Filter out existing logos
            df_filtered = df[~df['ID'].astype(str).isin(existing_ids)]
            filtered_count = len(df_filtered)
            skipped_count = initial_count - filtered_count
            
            logging.info(f"Found {skipped_count} existing logos, processing {filtered_count} remaining companies")
            print(f"📁 Found {skipped_count} existing logos, skipping...")
            print(f"🔄 Processing {filtered_count} remaining companies")
            
            return df_filtered
        else:
            logging.info(f"No existing logos found, processing all {initial_count} companies")
            return df

    def process_companies(self) -> None:
        """Process all companies to obtain their logos."""
        df = self.get_input_data()
        if df.empty:
            return

        # Filter out companies that already have logos
        df = self.filter_existing_logos(df)
        if df.empty:
            print("✅ All companies already have logos. Nothing to process!")
            return

        self.total_companies = len(df)
        total_batches = (len(df) + self.batch_size - 1) // self.batch_size
        
        print(f"\nProcessing {self.total_companies} companies in {total_batches} batches...")
        
        self.total_successful = 0
        self.total_failed = 0
        self.results = []
        batch_timings = []  # Track batch timings for ETA calculation

        for start_idx in range(0, len(df), self.batch_size):
            batch_df = df.iloc[start_idx:min(start_idx + self.batch_size, len(df))]
            batch_num = (start_idx // self.batch_size) + 1

            successful, total, results_df = process_batch(
                batch_df,
                self.output_folder,
                batch_idx=batch_num,
                total_batches=total_batches,
                batch_start_times=batch_timings
            )

            self.total_successful += successful
            self.total_failed += (total - successful)
            self.results.append(results_df)

    def _format_time(self, seconds: float) -> str:
        """Format time duration in a human-readable way."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def cleanup(self) -> None:
        """Clean up resources and print final statistics."""
        elapsed_time = time.time() - self.start_time
        processed_count = self.total_successful + self.total_failed
        success_rate = (self.total_successful / processed_count) * 100 if processed_count > 0 else 0
        
        print("\nProcessing Summary:")
        print(f"Total time: {self._format_time(elapsed_time)}")
        print(f"Companies processed: {processed_count}/{self.total_companies}")
        print(f"Success rate: {self.total_successful}/{processed_count} ({success_rate:.1f}%)")
