#!/usr/bin/env python3
"""
Company Logo Scraper - Main Entry Point
Consolidated entry point with CLI argument parsing and orchestration.
"""

import sys
import os
import argparse
from typing import Optional

# Add src to Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import version information
try:
    from src.__version__ import __version__, __description__
except ImportError:
    __version__ = "1.0.0"
    __description__ = "Company Logo Scraper"

from src.config import CONFIG
from src.logo_scraper_core import LogoScraper


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f'{__description__} v{__version__}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python main.py --input "C:\\Data\\input\\Companies.xlsx" --output "C:\\Data\\logo"
  python main.py --batch-size 500 --max-processes 4
  python main.py --filter "country=US" --filter "industry=Tech"
  python main.py --id 12345 --id 67890 --clean

Version: {__version__}
        """
    )

    parser.add_argument('--input', '-i',
                       help=f'Path to the input Excel file (default: {CONFIG["INPUT_FILE"]})')

    parser.add_argument('--output', '-o',
                       help=f'Output directory for logos (default: {CONFIG["OUTPUT_FOLDER"]})')

    parser.add_argument('--batch-size', '-b', type=int,
                       help=f'Number of companies to process in each batch (default: {CONFIG["BATCH_SIZE"]})')

    parser.add_argument('--max-processes', '-p', type=int,
                       help=f'Maximum number of parallel processes (default: {CONFIG["MAX_PROCESSES"]})')

    parser.add_argument('--filter', '-f', action='append',
                       help='Add a filter in format "column=value" (can be used multiple times)')

    parser.add_argument('--id', action='append',
                       help='Process only the specified ID (can be used multiple times)')

    return parser.parse_args()


def update_config_from_args(args: argparse.Namespace) -> None:
    """Update the CONFIG dictionary with command line arguments."""
    # Map CLI args to CONFIG keys
    arg_to_config = {
        'input': 'INPUT_FILE',
        'output': 'OUTPUT_FOLDER',
        'batch_size': 'BATCH_SIZE',
        'max_processes': 'MAX_PROCESSES',
    }
    for arg, config_key in arg_to_config.items():
        value = getattr(args, arg, None)
        if value is not None:
            CONFIG[config_key] = value

    # Process filters
    if args.filter:
        CONFIG['filters'] = CONFIG.get('filters', {})
        for filter_str in args.filter:
            try:
                column, value = filter_str.split('=', 1)
                CONFIG['filters'][column.lower()] = value
            except ValueError:
                print(f"Ignoring invalid filter format: {filter_str}")

    # Handle specific IDs if provided
    if args.id:
        CONFIG['id_filter'] = args.id


def main() -> None:
    """Main entry point for the Company Logo Scraper."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Update configuration with command line arguments
    update_config_from_args(args)
    
    # Create and run the logo scraper
    scraper: Optional[LogoScraper] = None
    try:
        scraper = LogoScraper(
            output_folder=CONFIG['OUTPUT_FOLDER'],
            batch_size=CONFIG['BATCH_SIZE']
        )
        scraper.process_companies()
        print("Logo scraping completed successfully!")
    except KeyboardInterrupt:
        print("Process interrupted by user")
    except Exception as e:
        print(f"Error in main process: {str(e)}")
        raise
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
