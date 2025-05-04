import os
import logging
import pandas as pd
from services.clearbit_service import ClearbitService
from services.duckduckgo_service import DuckDuckGoService
from services.favicon_service import FaviconService
from services.default_service import DefaultService
from utils.url_utils import clean_url, get_domain_from_url
from utils.image_utils import save_standardized_logo
from utils.progress_tracker import ProgressTracker
from config import CONFIG

class LogoScraper:
    def __init__(self, output_folder=CONFIG['OUTPUT_FOLDER'], batch_size=CONFIG['BATCH_SIZE']):
        self.output_folder = output_folder
        self.temp_folder = os.path.join(os.path.dirname(output_folder), 'temp')
        self.batch_size = batch_size
        
        # Create output and temp directories
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Initialize services with configuration
        self.duckduckgo = DuckDuckGoService(CONFIG['OUTPUT_SIZE'])
        self.favicon = FaviconService(CONFIG['OUTPUT_SIZE'])
        self.clearbit = ClearbitService(CONFIG['OUTPUT_SIZE'])
        self.default = DefaultService(CONFIG['OUTPUT_SIZE'])
        
        # Initialize progress tracker
        self.total_companies = 0
        self.progress = ProgressTracker()
        
    def process_company(self, row):
        """Process a single company row"""
        tpid = str(row['TPID'])
        
        # Skip if already processed
        if self.progress.is_processed(tpid):
            return True

        # Get company details - use TPAccountName as primary, fall back to CRMAccountName
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
            if not domain:
                continue
            
            # Try Clearbit first
            temp_data = self.clearbit.get_logo(domain)
            if temp_data:
                # Try to save and validate the logo
                temp_path = os.path.join(self.temp_folder, f"{tpid}_clearbit.png")
                if save_standardized_logo(temp_data, temp_path):
                    logo_data = temp_data
                    logo_source = "Clearbit"
                    os.remove(temp_path)
                    break
                elif os.path.exists(temp_path):
                    os.remove(temp_path)
                    
            # Try DuckDuckGo if Clearbit failed or image was too small
            if not logo_data:
                temp_data = self.duckduckgo.get_logo(domain)
                if temp_data:
                    # Try to save and validate the logo
                    temp_path = os.path.join(self.temp_folder, f"{tpid}_duckduckgo.png")
                    if save_standardized_logo(temp_data, temp_path):
                        logo_data = temp_data
                        logo_source = "DuckDuckGo"
                        os.remove(temp_path)
                        break
                    elif os.path.exists(temp_path):
                        os.remove(temp_path)

            # Try Favicon if both Clearbit and DuckDuckGo failed
            if not logo_data:
                temp_data = self.favicon.get_logo(domain)
                if temp_data:
                    # Try to save and validate the logo
                    temp_path = os.path.join(self.temp_folder, f"{tpid}_favicon.png")
                    if save_standardized_logo(temp_data, temp_path):
                        logo_data = temp_data
                        logo_source = "Favicon"
                        os.remove(temp_path)
                        break
                    elif os.path.exists(temp_path):
                        os.remove(temp_path)

        # Create default logo if no valid logo found and company name exists
        if not logo_data and company_name:
            logo_data = self.default.get_logo(company_name)
            logo_source = "Default"

        # Save final logo if found
        if logo_data:
            output_path = os.path.join(self.output_folder, f"{tpid}.png")
            if save_standardized_logo(logo_data, output_path):
                logging.info(f"Successfully saved logo for TPID {tpid} from {logo_source}")
                self.progress.mark_completed(tpid)
                return True

        logging.error(f"Failed to process logo for TPID {tpid}")
        self.progress.mark_failed(tpid)
        return False

    def process_batch(self, df):
        """Process a batch of companies"""
        total = len(df)
        completed = 0
        successful = 0
        
        for _, row in df.iterrows():
            completed += 1
            if self.process_company(row):
                successful += 1
                
            if completed % 10 == 0:
                success_rate = (successful / completed) * 100 if completed > 0 else 0
                total_completed = len(self.progress.progress['completed'])
                total_failed = len(self.progress.progress['failed'])
                total_processed = total_completed + total_failed
                overall_progress = (total_processed / self.total_companies * 100) if self.total_companies > 0 else 0
                
                logging.info(
                    f"Batch Progress: {completed}/{total} ({completed/total:.1%}). Success rate: {success_rate:.1f}%\n"
                    f"Overall Progress: {total_processed}/{self.total_companies} TPIDs processed ({overall_progress:.1f}%). "
                    f"Successful: {total_completed}, Failed: {total_failed}"
                )

def main():
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
    try:
        input_file = CONFIG['INPUT_FILE']
        logging.info(f"Reading {input_file} file...")
        df = pd.read_excel(input_file)
        logging.info(f"Successfully read {len(df):,} companies from {input_file}")
    except Exception as e:
        logging.error(f"Error reading {input_file}: {str(e)}")
        return
    
    # Create scraper
    scraper = LogoScraper()
    scraper.total_companies = len(df)  # Set total number of companies
    
    # Process in batches
    batch_size = scraper.batch_size
    for start_idx in range(0, len(df), batch_size):
        end_idx = min(start_idx + batch_size, len(df))
        batch_df = df.iloc[start_idx:end_idx]
        results = scraper.process_batch(batch_df)

if __name__ == "__main__":
    main()