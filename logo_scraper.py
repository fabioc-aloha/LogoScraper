"""Company Logo Scraper

This script automates the process of downloading, standardizing, and tracking company logos from various sources. It supports batch processing, filtering, progress tracking, and enriched data export. The script is configurable via command-line arguments and a config file, and is designed for robust, resumable operation.

Main Features:
- Reads company data from an Excel file, with optional filters and TPID selection.
- Processes companies in batches with parallelism and progress tracking.
- Downloads and standardizes logos, saving results and enriched metadata.
- Tracks completed and failed companies to avoid redundant work.
- Supports cleaning temporary files and resuming interrupted runs.
- Logs detailed progress, statistics, and errors to a log file.
- Exports enriched results to a timestamped Excel file with summary statistics.
- Robust domain cleaning: handles malformed/invalid domains, strips unwanted characters, and supports multiple delimiters.
- Enhanced diagnostics: detailed logging for logo fetch failures, including HTTP status and response content for Clearbit.

Command-line Arguments:
  --input, -i         Path to the input Excel file (overrides config)
  --output, -o        Output directory for logos (overrides config)
  --temp, -t          Temporary directory for processing (overrides config)
  --batch-size, -b    Number of companies per batch (overrides config)
  --log-level, -l     Logging level (DEBUG, INFO, etc.)
  --max-processes, -p Maximum parallel processes (overrides config)
  --top, -n           Process only the first N companies
  --clean, -c         Clean temporary files before starting
  --filter, -f        Add a filter in format "column=value" (can be used multiple times)
  --tpid              Process only the specified TPID(s) (can be used multiple times)

Workflow:
1. Parses command-line arguments and updates configuration.
2. Optionally cleans temporary files.
3. Initializes the LogoScraper, validates configuration, and sets up logging.
4. Loads and filters input data, excluding already processed companies.
5. Processes companies in batches, updating progress and saving enriched results.
6. On completion or interruption, saves state and outputs summary statistics.

See README.md for more details and usage examples.
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
    """
    Manages the company logo scraping and processing pipeline.

    Features:
    - Batch processing of company data with parallelism and progress tracking.
    - Robust domain cleaning: handles malformed/invalid domains, strips unwanted characters, and supports multiple delimiters.
    - Enhanced diagnostics: detailed logging for logo fetch failures, including HTTP status and response content for Clearbit.
    - Tracks completed and failed companies to avoid redundant work.
    - Exports enriched results to Excel with summary statistics.
    - Supports cleaning temporary files and resuming interrupted runs.
    - Configurable via command-line arguments and config file.
    """
    
    def __init__(self, batch_size=CONFIG['BATCH_SIZE']):
        """Initialize the LogoScraper with output directory and batch size."""
        self.start_time = time.time()
        self.output_folder = CONFIG['OUTPUT_FOLDER']
        self.temp_folder = CONFIG['TEMP_FOLDER']
        self.batch_size = batch_size

        # Remove the entire temp folder at initialization for a clean state
        if os.path.exists(self.temp_folder):
            try:
                shutil.rmtree(self.temp_folder)
            except Exception as e:
                print(f"Warning: Failed to remove temp folder {self.temp_folder}: {e}")
        
        self._setup_directories_and_logging()
        self._validate_config_and_load_cache()
        
        # Initialize components
        self.enriched_data = []
        self.progress = ProgressTracker(
            temp_folder=self.temp_folder,
            logos_folder=self.output_folder
        )
        self.total_companies = 0
        self.total_successful = 0
        self.total_failed = 0

    def _setup_directories_and_logging(self):
        """Create required directories and set up logging."""
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        
        setup_logging(self.temp_folder, CONFIG['LOG_FILENAME'])
        
        logging.info("=" * 80)
        logging.info(f"LOGO SCRAPER STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Output folder: {self.output_folder}")
        logging.info(f"Batch size: {self.batch_size}")
        logging.info(f"Target logo size: {CONFIG['OUTPUT_SIZE']}x{CONFIG['OUTPUT_SIZE']} pixels")
        logging.info("=" * 80)

    def _validate_config_and_load_cache(self):
        """Validate configuration and load failed domains cache."""
        validator = ConfigValidator(CONFIG)
        if not validator.validate():
            logging.error("Invalid configuration, exiting")
            sys.exit(1)
        self.failed_domains = self._load_failed_domains_cache()

    def _load_failed_domains_cache(self):
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

    def _save_failed_domains_cache(self):
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
        
        self._log_batch_progress_summary(batch_idx, total_batches)
        
        return successful, total, enriched_df

    def _log_batch_progress_summary(self, batch_idx, total_batches):
        """Logs the progress summary after each batch."""
        overall_processed_count = batch_idx * self.batch_size 
        overall_processed_count = min(overall_processed_count, self.total_companies) # Cap at total_companies

        overall_percent = (overall_processed_count / self.total_companies) * 100 if self.total_companies > 0 else 0
        overall_percent = min(overall_percent, 100.0) # Cap at 100%
            
        current_processed_in_session = self.total_successful + self.total_failed
        success_rate = (self.total_successful / current_processed_in_session) * 100 if current_processed_in_session > 0 else 0
        
        elapsed_time = time.time() - self.start_time
        
        # Estimate time remaining
        if batch_idx < total_batches and current_processed_in_session > 0:
            # Use items processed in this session for ETA if more accurate
            items_per_second_session = current_processed_in_session / elapsed_time
            remaining_items = self.total_companies - overall_processed_count
            if items_per_second_session > 0:
                remaining_time_seconds = remaining_items / items_per_second_session
                remaining_str = self._format_time(remaining_time_seconds)
            else:
                remaining_str = "Calculating..."
        elif batch_idx == total_batches:
            remaining_str = "Complete"
        else:
            remaining_str = "Calculating..."

        logging.info(f"Progress Summary: Batch {batch_idx}/{total_batches} ({overall_percent:.1f}%) | " +
                     f"Session Success: {success_rate:.1f}% ({self.total_successful}/{current_processed_in_session}) | " +
                     f"Elapsed: {self._format_time(elapsed_time)} | ETA: {remaining_str}")

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
        """Clean up resources and save final state. Also generate logo provenance stats."""
        self._save_failed_domains_cache()
        self.save_enriched_data()
        self._generate_logo_provenance_stats()
        elapsed_time = time.time() - self.start_time
        processed_in_session = self.total_successful + self.total_failed
        success_rate_session = (self.total_successful / processed_in_session) * 100 if processed_in_session > 0 else 0
        self._log_completion_summary(elapsed_time, processed_in_session, success_rate_session)

    def _generate_logo_provenance_stats(self):
        """Analyze enriched data and log stats on logo provenance (source breakdown and favicon provider details)."""
        if not self.enriched_data:
            logging.info("No enriched data to analyze for logo provenance stats.")
            return
        import pandas as pd
        all_df = pd.concat(self.enriched_data, ignore_index=True)
        if 'LogoSource' not in all_df.columns:
            logging.info("No LogoSource column found in enriched data for provenance stats.")
            return
        source_counts = all_df['LogoSource'].value_counts().to_dict()
        total = sum(source_counts.values())
        logging.info("Logo Provenance Stats (source breakdown):")
        for source, count in source_counts.items():
            percent = (count / total) * 100 if total > 0 else 0
            logging.info(f"  {source}: {count} ({percent:.1f}%)")
        logging.info(f"  Total: {total}")
        # --- Enhanced favicon provider stats ---
        favicon_rows = all_df[all_df['LogoSource'].str.contains('DuckDuckGo|Google S2', na=False)]
        if not favicon_rows.empty:
            provider_stats = favicon_rows['LogoSource'].str.extract(r'(DuckDuckGo|Google S2)')
            favicon_rows = favicon_rows.assign(FaviconProvider=provider_stats[0])
            provider_counts = favicon_rows['FaviconProvider'].value_counts().to_dict()
            logging.info("Favicon Provider Breakdown (largest logo chosen):")
            for provider, count in provider_counts.items():
                logging.info(f"  {provider}: {count}")
            # If logo size is available, report average size per provider
            if 'LogoSize' in favicon_rows.columns:
                avg_sizes = favicon_rows.groupby('FaviconProvider')['LogoSize'].mean().to_dict()
                for provider, avg_size in avg_sizes.items():
                    logging.info(f"  {provider} average logo size: {avg_size:.1f} bytes")
        else:
            logging.info("No favicon provider logos found in enriched data.")

    def _log_completion_summary(self, elapsed_time, processed_count, success_rate):
        """Logs the final summary of the scraping process for the current session."""
        logging.info("=" * 80)
        logging.info(f"LOGO SCRAPER SESSION COMPLETED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total session time: {self._format_time(elapsed_time)}")
        logging.info(f"Companies processed in this session: {processed_count}")
        logging.info(f"Success rate for this session: {self.total_successful}/{processed_count} ({success_rate:.1f}%)")
        
        if self.enriched_data:
            # Consolidate all enriched data for final source breakdown
            all_session_df = pd.concat(self.enriched_data, ignore_index=True)
            if not all_session_df.empty:
                source_counts = all_session_df['LogoSource'].value_counts().to_dict()
                summary = ", ".join(f"{src}: {cnt}" for src, cnt in source_counts.items())
                logging.info(f"Sources for logos processed in this session: {summary}")
        logging.info("=" * 80)

    def get_input_data(self):
        """Loads, filters, and prepares input data from the Excel file."""
        input_file = CONFIG['INPUT_FILE']
        logging.info(f"Reading input data from: {input_file}")
        
        input_service = InputDataService()
        df = input_service.get_data(
            filters=CONFIG.get('filters'),
            top_n=CONFIG.get('TOP_N')
        )
        
        df = self._apply_tpid_filter(df)
        self._log_input_data_stats(df)
        return df

    def _apply_tpid_filter(self, df):
        """Applies TPID filter if specified in config."""
        if 'tpid_filter' in CONFIG and CONFIG['tpid_filter']:
            tpids = CONFIG['tpid_filter']
            logging.info(f"Filtering to specific TPIDs: {', '.join(tpids)}")
            original_count = len(df)
            df = df[df['tpid'].astype(str).isin(tpids)]
            logging.info(f"Filtered {original_count} companies down to {len(df)} based on TPID list.")
            if len(df) == 0:
                logging.error(f"No companies found with the specified TPIDs. Exiting.")
                sys.exit(1)
            elif len(df) < len(tpids):
                found_tpids = df['tpid'].astype(str).tolist()
                missing = [tpid for tpid in tpids if tpid not in found_tpids]
                logging.warning(f"Could not find data for these TPIDs: {', '.join(missing)}")
        return df

    def _log_input_data_stats(self, df):
        """Logs statistics about the loaded input data."""
        companies_with_urls = df['websiteurl'].notna() & (df['websiteurl'] != '')
        url_count = companies_with_urls.sum()
        url_percentage = (url_count / len(df)) * 100 if len(df) > 0 else 0
        
        logging.info(f"Successfully read and filtered {len(df):,} companies from input file")
        logging.info(f"Companies with website URLs: {url_count:,} ({url_percentage:.1f}%)")

    def _filter_unprocessed_companies(self, df):
        """Filters out already processed companies."""
        df['tpid'] = df['tpid'].astype(str)
        already_completed = self.progress.progress['completed']
        already_failed = self.progress.progress['failed']
        
        logging.info(f"Previously processed: {len(already_completed):,} completed, {len(already_failed):,} failed (will be skipped)")
        
        unprocessed_df = df[~df['tpid'].isin(already_completed + already_failed)]
        
        num_unprocessed = len(unprocessed_df)
        if num_unprocessed == 0:
            logging.info("No new companies to process from the filtered input.")
            return pd.DataFrame() # Return empty DataFrame
            
        logging.info(f"Found {num_unprocessed:,} companies to process in this session.")
        return unprocessed_df

    def process_companies(self):
        """Main loop to process all companies."""
        input_df = self.get_input_data()
        
        # This total_companies refers to the total from the input file after initial filters (top_n, column filters, tpid_filter)
        # It's used for overall progress calculation relative to the initial dataset.
        self.total_companies = len(input_df) 
        logging.info(f"Total companies after initial loading and filtering: {self.total_companies:,}")

        unprocessed_df = self._filter_unprocessed_companies(input_df)
        
        num_to_process_this_session = len(unprocessed_df)
        if num_to_process_this_session == 0:
            return # Already logged in _filter_unprocessed_companies

        total_batches = (num_to_process_this_session + self.batch_size - 1) // self.batch_size
        logging.info(f"Will process {num_to_process_this_session:,} companies in {total_batches} batches of up to {self.batch_size} each.")
        
        for start_idx in range(0, num_to_process_this_session, self.batch_size):
            batch_num = (start_idx // self.batch_size) + 1
            end_idx = min(start_idx + self.batch_size, num_to_process_this_session)
            batch_df = unprocessed_df.iloc[start_idx:end_idx]
            
            successful_in_batch, total_in_batch, enriched_df_batch = self.process_batch(batch_df, batch_num, total_batches)
            
            # Update progress tracker based on batch results
            if not enriched_df_batch.empty:
                batch_tpids = enriched_df_batch['TPID'].tolist() # Assuming TPID is a column after processing
                batch_results = enriched_df_batch['LogoGenerated'].tolist()
            
                for tpid, success in zip(batch_tpids, batch_results):
                    if success:
                        self.progress.mark_completed(str(tpid))
                    else:
                        self.progress.mark_failed(str(tpid))
            
            # Log batch completion details
            source_counts_batch = enriched_df_batch['LogoSource'].value_counts().to_dict() if not enriched_df_batch.empty else {}
            
            # Overall progress stats refers to the total number of companies in the input file.
            # This gives a sense of how much of the *entire dataset* is done.
            overall_completed_count = len(self.progress.progress['completed'])
            overall_failed_count = len(self.progress.progress['failed'])
            total_ever_processed = overall_completed_count + overall_failed_count
            overall_dataset_progress_percent = (total_ever_processed / self.total_companies) * 100 if self.total_companies > 0 else 0
            overall_dataset_progress_percent = min(overall_dataset_progress_percent, 100.0)


            logging.info(
                f"Batch {batch_num}/{total_batches} complete: {successful_in_batch}/{total_in_batch} successful. "
                f"Sources: {source_counts_batch}. "
                f"Overall dataset processed: {total_ever_processed}/{self.total_companies} ({overall_dataset_progress_percent:.1f}%)"
            )
    
    def clean_temporary_data(self, force_clean=False):
        """Cleans temporary files and folders."""
        import logging
        temp_folder_path = self.temp_folder # Use instance variable
        
        user_confirmed_clean = force_clean
        if not user_confirmed_clean and os.path.exists(temp_folder_path) and os.listdir(temp_folder_path):
            try:
                resp = input(f"Temporary files detected in {temp_folder_path}. Clear them? [y/N]: ")
                if resp.strip().lower() == 'y':
                    user_confirmed_clean = True
            except EOFError: # Handle non-interactive environments
                 logging.warning("No input available for temp cleaning prompt, defaulting to not cleaning.")
                 user_confirmed_clean = False


        if user_confirmed_clean:
            logging.info(f"Cleaning temporary folder: {temp_folder_path}")
            # Shutdown logging to release file handles before deleting log files
            try:
                logging.shutdown()
                # Remove all handlers from the root logger to ensure file handles are released (especially on Windows)
                import logging as _logging
                for handler in list(_logging.getLogger().handlers):
                    _logging.getLogger().removeHandler(handler)
            except Exception:
                pass
            for item in os.listdir(temp_folder_path):
                path = os.path.join(temp_folder_path, item)
                try:
                    # Only remove files that are not .png (logo outputs)
                    if os.path.isfile(path) or os.path.islink(path):
                        if not path.lower().endswith('.png'):
                            os.remove(path)
                            logging.debug(f"Removed temporary file: {path}")
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                        logging.debug(f"Removed temporary directory: {path}")
                except Exception as e:
                    logging.error(f"Failed to remove {path}: {e}")
            # Recreate the temp folder as it's expected to exist by other parts of the code
            os.makedirs(temp_folder_path, exist_ok=True)
            logging.info("Temporary folder cleared and recreated.")
        else:
            logging.info("Temporary data cleaning skipped.")


def main():
    """Main entry point for the logo scraper."""
    args = parse_arguments()
    update_config_from_args(args)
    
    scraper = None
    try:
        # Instantiate scraper first to use its methods, including logging setup within __init__
        scraper = LogoScraper(
        )
        
        # Perform cleaning using the scraper's method
        scraper.clean_temporary_data(force_clean=args.clean)
        
        scraper.process_companies()
        
    except KeyboardInterrupt:
        logging.info("Process interrupted by user.")
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise
    finally:
        if scraper:
            scraper.cleanup()
        # Ensure logging is shutdown at the end of the script
        import logging
        try:
            logging.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    main()