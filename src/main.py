"""
Main entry point for the Company Logo Scraper pipeline.
"""
from typing import Optional
from src.config import CONFIG
from src.cli import parse_arguments, update_config_from_args
from src.logo_scraper_core import LogoScraper

def main() -> None:
    """Main entry point for the Company Logo Scraper."""
    args = parse_arguments()
    update_config_from_args(args)
    
    scraper: Optional[LogoScraper] = None
    try:
        scraper = LogoScraper(
            output_folder=CONFIG['OUTPUT_FOLDER'],
            batch_size=CONFIG['BATCH_SIZE']
        )
        scraper.process_companies()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\nError in main process: {str(e)}")
        raise
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()
