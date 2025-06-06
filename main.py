#!/usr/bin/env python3
"""
Company Logo Scraper - Main Entry Point
Consolidated entry point with CLI argument parsing and orchestration.
"""

import sys
import os
import argparse
import logging
from typing import Optional

# Add src to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import version information
try:
    from __version__ import __version__, __description__
except ImportError:
    __version__ = "1.0.0"
    __description__ = "Company Logo Scraper"

from src.config import CONFIG
from src.logo_scraper_core import LogoScraper
from src.cleanup import clean_temp_folder
from src.utils.log_config import setup_logging


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f'{__description__} v{__version__}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python main.py --input "C:\\Data\\input\\Companies.xlsx" --output "C:\\Data\\logo"
  python main.py --batch-size 500 --max-processes 4 --log-level INFO
  python main.py --filter "country=US" --filter "industry=Tech" --top 100
  python main.py --tpid 12345 --tpid 67890 --clean

Version: {__version__}
        """
    )

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


def update_config_from_args(args: argparse.Namespace) -> None:
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


def main() -> None:
    """Main entry point for the Company Logo Scraper."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Update configuration with command line arguments
    update_config_from_args(args)
    
    # Setup logging with the potentially updated log level
    setup_logging(CONFIG['TEMP_FOLDER'], CONFIG['LOG_FILENAME'])
    
    # Handle temp folder cleanup
    temp_folder = CONFIG['TEMP_FOLDER']
    clean_temp = args.clean
    
    try:
        if not clean_temp and os.path.exists(temp_folder) and os.listdir(temp_folder):
            logging.info(f"Temporary files detected in {temp_folder}. Prompting user for cleanup.")
            resp = input(f"Temporary files detected in {temp_folder}. Clear them? [y/N]: ")
            logging.info(f"User response to temp cleanup prompt: {resp}")
            clean_temp = resp.strip().lower() == 'y'
        
        if clean_temp:
            clean_temp_folder(temp_folder)
    except KeyboardInterrupt:
        logging.info("Startup interrupted by user")
        return
    
    # Create and run the logo scraper
    scraper: Optional[LogoScraper] = None
    try:
        scraper = LogoScraper(
            output_folder=CONFIG['OUTPUT_FOLDER'],
            batch_size=CONFIG['BATCH_SIZE']
        )
        scraper.process_companies()
        logging.info("Logo scraping completed successfully!")
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
