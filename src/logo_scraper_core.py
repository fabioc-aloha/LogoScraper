import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Optional
import pandas as pd
from src.utils.progress_tracker import ProgressTracker
from src.utils.batch_processor import process_batch
from src.utils.log_config import setup_logging
from src.utils.config_validator import ConfigValidator
from src.services.input_data_service import InputDataService
from src.config import CONFIG

class LogoScraper:
    """
    Manages the company logo scraping and processing pipeline.
    """
    def __init__(self, output_folder: str = CONFIG['OUTPUT_FOLDER'], batch_size: int = CONFIG['BATCH_SIZE']):
        self.start_time = time.time()
        self.output_folder = output_folder
        self.temp_folder = CONFIG['TEMP_FOLDER']
        self.batch_size = batch_size
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        setup_logging(self.temp_folder, CONFIG['LOG_FILENAME'])
        logging.info("=" * 80)
        logging.info(f"LOGO SCRAPER STARTED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Output folder: {output_folder}")
        logging.info(f"Batch size: {batch_size}")
        logging.info(f"Target logo size: {CONFIG['OUTPUT_SIZE']}x{CONFIG['OUTPUT_SIZE']} pixels")
        logging.info("=" * 80)
        validator = ConfigValidator(CONFIG)
        if not validator.validate():
            logging.error("Invalid configuration, exiting")
            sys.exit(1)
        self.enriched_data = []
        self.failed_domains = self._load_failed_domains()
        self.progress = ProgressTracker(
            temp_folder=self.temp_folder,
            logos_folder=self.output_folder
        )
        self.total_companies = 0
        self.total_successful = 0
        self.total_failed = 0

    def _load_failed_domains(self) -> set:
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

    def _save_failed_domains(self) -> None:
        cache_file = os.path.join(self.temp_folder, CONFIG['FAILED_DOMAINS_CACHE_FILE'])
        try:
            with open(cache_file, 'w') as f:
                json.dump(list(self.failed_domains), f)
                logging.info(f"Saved {len(self.failed_domains)} failed domains to cache")
        except Exception as e:
            logging.error(f"Error saving failed domains cache: {str(e)}")

    def process_batch(self, df: pd.DataFrame, batch_idx: int, total_batches: int) -> tuple:
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
        overall_percent = ((batch_idx * self.batch_size) / self.total_companies) * 100
        if overall_percent > 100:
            overall_percent = 100
        success_rate = (self.total_successful / (self.total_successful + self.total_failed)) * 100 if (self.total_successful + self.total_failed) > 0 else 0
        elapsed_time = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed_time)
        if batch_idx < total_batches:
            completed_fraction = batch_idx / total_batches
            if completed_fraction > 0:
                total_estimated_time = elapsed_time / completed_fraction
                remaining_time = total_estimated_time - elapsed_time
                remaining_str = self._format_time(remaining_time)
            else:
                remaining_str = "Unknown"
        else:
            remaining_str = "Complete"
        logging.info(
            f"Progress Summary: {batch_idx}/{total_batches} batches ({overall_percent:.1f}%) | "
            f"Success rate: {success_rate:.1f}% | "
            f"Elapsed: {elapsed_str} | Remaining: {remaining_str}"
        )
        return successful, total, enriched_df

    def _format_time(self, seconds: float) -> str:
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def save_enriched_data(self) -> None:
        if not self.enriched_data:
            logging.warning("No enriched data to save")
            return
        final_df = pd.concat(self.enriched_data, ignore_index=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = CONFIG['ENRICHED_FILENAME_PREFIX']
        output_file = os.path.join(
            os.path.dirname(CONFIG['INPUT_FILE']),
            f"{prefix}{timestamp}.xlsx"
        )
        source_summary = final_df['LogoSource'].value_counts().to_dict()
        summary_str = ", ".join([f"{source}: {count}" for source, count in source_summary.items()])
        final_df.to_excel(output_file, index=False)
        logging.info(f"Saved enriched data to {output_file}")
        logging.info(f"Logo source summary: {summary_str}")

    def cleanup(self) -> None:
        self._save_failed_domains()
        self.save_enriched_data()
        elapsed_time = time.time() - self.start_time
        processed_count = self.total_successful + self.total_failed
        success_rate = (self.total_successful / processed_count) * 100 if processed_count > 0 else 0
        logging.info("=" * 80)
        logging.info(f"LOGO SCRAPER COMPLETED AT {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total time: {self._format_time(elapsed_time)}")
        logging.info(f"Companies processed: {processed_count}/{processed_count}")
        logging.info(f"Success rate: {self.total_successful}/{processed_count} ({success_rate:.1f}%)")
        if self.enriched_data:
            all_df = pd.concat(self.enriched_data, ignore_index=True)
            source_counts = all_df['LogoSource'].value_counts().to_dict()
            summary = ", ".join(f"{src}: {cnt}" for src, cnt in source_counts.items())
            logging.info(f"Final sources breakdown: {summary}")
        logging.info("=" * 80)

    def get_input_data(self) -> pd.DataFrame:
        input_file = CONFIG['INPUT_FILE']
        logging.info(f"Reading input data from: {input_file}")
        input_service = InputDataService()
        df = input_service.get_data(
            filters=CONFIG.get('filters'),
            top_n=CONFIG.get('TOP_N')
        )
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
        companies_with_urls = df['websiteurl'].notna() & (df['websiteurl'] != '')
        url_count = companies_with_urls.sum()
        url_percentage = (url_count / len(df)) * 100 if len(df) > 0 else 0
        logging.info(f"Successfully read {len(df):,} companies from input file")
        logging.info(f"Companies with website URLs: {url_count:,} ({url_percentage:.1f}%)")
        return df

    def process_companies(self) -> None:
        df = self.get_input_data()
        self.total_companies = len(df)
        logging.info(f"Total companies after filtering: {self.total_companies:,}")
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
        total_batches = (num_unprocessed + self.batch_size - 1) // self.batch_size
        logging.info(f"Will process in {total_batches} batches of {self.batch_size} companies each")
        for start_idx in range(0, num_unprocessed, self.batch_size):
            batch_num = (start_idx // self.batch_size) + 1
            end_idx = min(start_idx + self.batch_size, num_unprocessed)
            batch_df = unprocessed_df.iloc[start_idx:end_idx]
            successful, total, enriched_df = self.process_batch(batch_df, batch_num, total_batches)
            batch_tpids = batch_df['tpid'].tolist()
            batch_results = enriched_df['LogoGenerated'].tolist()
            for tpid, success in zip(batch_tpids, batch_results):
                if success:
                    self.progress.mark_completed(tpid)
                else:
                    self.progress.mark_failed(tpid)
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
