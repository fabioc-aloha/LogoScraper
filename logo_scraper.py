"""Company Logo Scraper

This module provides functionality to automatically download and standardize company logos
from various sources. It coordinates the overall process flow and orchestration.
"""

import os
import logging
import pandas as pd
import json
import sys
import shutil
import time
import argparse
from datetime import datetime
from utils.progress_tracker import ProgressTracker
from utils.filter_utils import apply_filters
from utils.batch_processor import process_batch
from utils.log_config import setup_logging
from utils.config_validator import ConfigValidator
from services.input_data_service import InputDataService
from config import CONFIG

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Company Logo Scraper')
    
    parser.add_argument('--input', '-i', 
                      help=f'Path to the input Excel file (default: {CONFIG["INPUT_FILE"]})')
    
    parser.add_argument('--output', '-o', 
                      help=f'Output directory for logos (default: {CONFIG["OUTPUT_FOLDER"]})')
    
    parser.add_argument('--temp', '-t', 
                      help=f'Temporary directory for processing files (default: {CONFIG["TEMP_FOLDER"]})')
    
    parser.add_argument('--batch-size', '-b', type=int, 
                      help=f'Number of companies to process in each batch (default: {CONFIG["BATCH_SIZE"]})')
    
    parser.add_argument('--log-level', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help=f'Logging level (default: {CONFIG["LOG_LEVEL"]})')
    
    parser.add_argument('--max-processes', '-p', type=int,
                      help=f'Maximum number of parallel processes (default: {CONFIG["MAX_PROCESSES"]})')
    
    parser.add_argument('--top', '-n', type=int,
                      help=f'Process only the first N companies (default: {CONFIG.get("TOP_N", "all")})')
    
    parser.add_argument('--clean', '-c', action='store_true',
                      help='Clean temporary files before starting')
    
    parser.add_argument('--filter', '-f', action='append',
                      help='Add a filter in format "column=value" (can be used multiple times)')
                      
    parser.add_argument('--tpid', action='append',
                      help='Process only the specified TPID (can be used multiple times)')
    
    return parser.parse_args()

def update_config_from_args(args):
    """Update the CONFIG dictionary with command line arguments."""
    if args.input:
        CONFIG['INPUT_FILE'] = args.input
    
    if args.output:
        CONFIG['OUTPUT_FOLDER'] = args.output
    
    if args.temp:
        CONFIG['TEMP_FOLDER'] = args.temp
    
    if args.batch_size:
        CONFIG['BATCH_SIZE'] = args.batch_size
    
    if args.log_level:
        CONFIG['LOG_LEVEL'] = args.log_level
    
    if args.max_processes:
        CONFIG['MAX_PROCESSES'] = args.max_processes
    
    if args.top:
        CONFIG['TOP_N'] = args.top
        
    # Process filters
    if args.filter:
        if 'filters' not in CONFIG:
            CONFIG['filters'] = {}
        
        for filter_str in args.filter:
            try:
                column, value = filter_str.split('=', 1)
                CONFIG['filters'][column.lower()] = value
            except ValueError:
                logging.warning(f"Ignoring invalid filter format: {filter_str}")
                
    # Handle specific TPIDs if provided
    if args.tpid:
        # Create a filter for specific TPIDs
        CONFIG['tpid_filter'] = args.tpid

class LogoScraper:
    """A class to manage the logo scraping and processing pipeline."""
    
    def __init__(self, output_folder=CONFIG['OUTPUT_FOLDER'], batch_size=CONFIG['BATCH_SIZE']):
        """Initialize the LogoScraper with output directory and batch size."""
        self.start_time = time.time()
        self.output_folder = output_folder
        self.temp_folder = CONFIG['TEMP_FOLDER']
        self.batch_size = batch_size
        
        # Create required directories
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Set up logging
        setup_logging(self.temp_folder, CONFIG['LOG_FILENAME'])
        
        # Log initial startup information
        logging.info("=" * 80)
        logging.info(f"LOGO SCRAPER STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Output folder: {output_folder}")
        logging.info(f"Batch size: {batch_size}")
        logging.info(f"Target logo size: {CONFIG['OUTPUT_SIZE']}x{CONFIG['OUTPUT_SIZE']} pixels")
        logging.info("=" * 80)
        
        # Validate configuration
        validator = ConfigValidator(CONFIG)
        if not validator.validate():
            logging.error("Invalid configuration, exiting")
            sys.exit(1)
        
        # Initialize components
        self.enriched_data = []
        self.failed_domains = self._load_failed_domains()
        self.progress = ProgressTracker(
            temp_folder=self.temp_folder,
            logos_folder=self.output_folder
        )
        self.total_companies = 0
        self.total_successful = 0
        self.total_failed = 0

    def _load_failed_domains(self):
        """Load the cache of failed domains from disk."""
        cache_file = os.path.join(self.temp_folder, CONFIG['FAILED_DOMAINS_CACHE_FILE'])
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    domains = set(json.load(f))
                    logging.info(f"Loaded {len(domains)} previously failed domains")
                    return domains
            except Exception as e:
                logging.error(f"Error loading failed domains cache: {str(e)}")
                return set()
        return set()

    def _save_failed_domains(self):
        """Save the cache of failed domains to disk."""
        cache_file = os.path.join(self.temp_folder, CONFIG['FAILED_DOMAINS_CACHE_FILE'])
        try:
            with open(cache_file, 'w') as f:
                json.dump(list(self.failed_domains), f)
                logging.info(f"Saved {len(self.failed_domains)} failed domains to cache")
        except Exception as e:
            logging.error(f"Error saving failed domains cache: {str(e)}")

    def process_batch(self, df, batch_idx, total_batches):
        """Run parallel batch processing and return both results and enriched data."""
        logging.info(f"Starting batch {batch_idx}/{total_batches} - {len(df)} companies")
        
        successful, total, enriched_df = process_batch(
            companies_df=df,
            output_folder=self.output_folder,
            temp_folder=self.temp_folder,
            batch_idx=batch_idx,
            total_batches=total_batches
        )
        
        self.total_successful += successful
        self.total_failed += (total - successful)
        self.enriched_data.append(enriched_df)
        
        # Update overall progress statistics
        overall_percent = ((batch_idx * self.batch_size) / self.total_companies) * 100
        if overall_percent > 100:
            overall_percent = 100
            
        success_rate = (self.total_successful / (self.total_successful + self.total_failed)) * 100 if (self.total_successful + self.total_failed) > 0 else 0
        
        # Calculate elapsed time and estimated time remaining
        elapsed_time = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed_time)
        
        if batch_idx < total_batches:
            # Estimate time remaining based on current progress
            completed_fraction = batch_idx / total_batches
            if completed_fraction > 0:
                total_estimated_time = elapsed_time / completed_fraction
                remaining_time = total_estimated_time - elapsed_time
                remaining_str = self._format_time(remaining_time)
            else:
                remaining_str = "Unknown"
        else:
            remaining_str = "Complete"
            
        logging.info(f"Progress Summary: {batch_idx}/{total_batches} batches ({overall_percent:.1f}%) | " +
                     f"Success rate: {success_rate:.1f}% | " +
                     f"Elapsed: {elapsed_str} | Remaining: {remaining_str}")
        
        return successful, total, enriched_df

    def _format_time(self, seconds):
        """Format time in seconds to a human-readable string."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def save_enriched_data(self):
        """Save the enriched dataset to Excel."""
        if not self.enriched_data:
            logging.warning("No enriched data to save")
            return
            
        # Combine all batches
        final_df = pd.concat(self.enriched_data, ignore_index=True)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = CONFIG['ENRICHED_FILENAME_PREFIX']
        output_file = os.path.join(
            os.path.dirname(CONFIG['INPUT_FILE']), 
            f"{prefix}{timestamp}.xlsx"
        )
        
        # Add summary statistics to the dataframe
        source_summary = final_df['LogoSource'].value_counts().to_dict()
        summary_str = ", ".join([f"{source}: {count}" for source, count in source_summary.items()])
        
        final_df.to_excel(output_file, index=False)
        
        logging.info(f"Saved enriched data to {output_file}")
        logging.info(f"Logo source summary: {summary_str}")

    def cleanup(self):
        """Clean up resources and save final state."""
        self._save_failed_domains()
        self.save_enriched_data()
        
        # Log final summary
        elapsed_time = time.time() - self.start_time
        success_rate = (self.total_successful / self.total_companies) * 100 if self.total_companies > 0 else 0
        
        logging.info("=" * 80)
        logging.info(f"LOGO SCRAPER COMPLETED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total time: {self._format_time(elapsed_time)}")
        logging.info(f"Companies processed: {self.total_successful + self.total_failed}/{self.total_companies}")
        logging.info(f"Success rate: {self.total_successful}/{self.total_companies} ({success_rate:.1f}%)")
        logging.info("=" * 80)

    def get_input_data(self):
        """Get input data from the Excel file."""
        input_file = CONFIG['INPUT_FILE']
        logging.info(f"Reading input data from: {input_file}")
        
        # Use input data service for consistent data handling
        input_service = InputDataService()
        df = input_service.get_data(
            filters=CONFIG.get('filters'),
            top_n=CONFIG.get('TOP_N')
        )
        
        # Apply TPID filter if specified
        if 'tpid_filter' in CONFIG and CONFIG['tpid_filter']:
            tpids = CONFIG['tpid_filter']
            logging.info(f"Filtering to specific TPIDs: {', '.join(tpids)}")
            df = df[df['tpid'].astype(str).isin(tpids)]
            if len(df) == 0:
                logging.error(f"No companies found with the specified TPIDs")
                sys.exit(1)
            elif len(df) < len(tpids):
                found_tpids = df['tpid'].astype(str).tolist()
                missing = [tpid for tpid in tpids if tpid not in found_tpids]
                logging.warning(f"Could not find these TPIDs: {', '.join(missing)}")
        
        # Log some statistics about the input data
        companies_with_urls = df['websiteurl'].notna() & (df['websiteurl'] != '')
        url_count = companies_with_urls.sum()
        url_percentage = (url_count / len(df)) * 100 if len(df) > 0 else 0
        
        logging.info(f"Successfully read {len(df):,} companies from input file")
        logging.info(f"Companies with website URLs: {url_count:,} ({url_percentage:.1f}%)")
        
        return df

    def process_companies(self):
        """Process all unprocessed companies."""
        # Get and filter input data
        df = self.get_input_data()
        self.total_companies = len(df)
        logging.info(f"Total companies after filtering: {self.total_companies:,}")
        
        # Filter out already processed companies
        df['tpid'] = df['tpid'].astype(str)
        already_completed = self.progress.progress['completed']
        already_failed = self.progress.progress['failed']
        
        logging.info(f"Previously processed: {len(already_completed):,} completed, {len(already_failed):,} failed")
        
        unprocessed_df = df[~df['tpid'].isin(already_completed + already_failed)]
        
        num_unprocessed = len(unprocessed_df)
        if num_unprocessed == 0:
            logging.info("No new companies to process")
            return
            
        logging.info(f"Found {num_unprocessed:,} unprocessed companies")
        
        # Process in batches
        total_batches = (num_unprocessed + self.batch_size - 1) // self.batch_size
        logging.info(f"Will process in {total_batches} batches of {self.batch_size} companies each")
        
        for start_idx in range(0, num_unprocessed, self.batch_size):
            batch_num = (start_idx // self.batch_size) + 1
            end_idx = min(start_idx + self.batch_size, num_unprocessed)
            batch_df = unprocessed_df.iloc[start_idx:end_idx]
            
            successful, total, enriched_df = self.process_batch(batch_df, batch_num, total_batches)
            
            # Update completed and failed lists in the progress tracker
            batch_tpids = batch_df['tpid'].tolist()
            batch_results = enriched_df['LogoGenerated'].tolist()
            
            for tpid, success in zip(batch_tpids, batch_results):
                if success:
                    self.progress.mark_completed(tpid)
                else:
                    self.progress.mark_failed(tpid)
            
            # Log batch completion
            source_counts = enriched_df['LogoSource'].value_counts().to_dict()
            overall_completed = len(self.progress.progress['completed'])
            overall_failed = len(self.progress.progress['failed'])
            overall_progress = (overall_completed + overall_failed) / self.total_companies * 100
            
            logging.info(
                f"Batch {batch_num}/{total_batches} complete: {successful}/{total} successful | "
                f"Source breakdown: {source_counts} | "
                f"Overall: {overall_completed + overall_failed}/{self.total_companies} "
                f"({overall_progress:.1f}%)"
            )

def main():
    """Main entry point for the logo scraper."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Update config with command line arguments
    update_config_from_args(args)
    
    scraper = None
    # Handle temp file cleaning if requested via command line or prompt
    temp_folder = CONFIG['TEMP_FOLDER']
    clean_temp = args.clean
    
    try:
        if not clean_temp and os.path.exists(temp_folder) and os.listdir(temp_folder):
            resp = input(f"Temporary files detected in {temp_folder}. Clear them? [y/N]: ")
            clean_temp = resp.strip().lower() == 'y'
            
        if clean_temp:
            for item in os.listdir(temp_folder):
                path = os.path.join(temp_folder, item)
                try:
                    if os.path.isfile(path) or os.path.islink(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                except Exception as e:
                    print(f"Failed to remove {path}: {e}")
            print("Temporary folder cleared.")
    except KeyboardInterrupt:
        print("Startup interrupted by user")
        return
        
    try:
        scraper = LogoScraper(
            output_folder=CONFIG['OUTPUT_FOLDER'],
            batch_size=CONFIG['BATCH_SIZE']
        )
        scraper.process_companies()
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()