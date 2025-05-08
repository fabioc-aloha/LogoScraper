"""Batch Processing Module

This module handles the parallel processing of company batches.
Simplified to focus on core parallel processing functionality.
"""

import os
import logging
import time
from multiprocessing import Pool
import pandas as pd
from utils.company_processor import CompanyProcessor
from utils.enrichment import enrich_batch_results
from config import CONFIG

def process_company_wrapper(args):
    """Wrapper function for processing a single company in parallel."""
    row, output_folder, temp_folder, batch_idx, total_batches, company_idx, batch_size = args
    
    try:
        tpid = str(row['tpid'])
        company_name = row.get('crmaccountname', '').strip()
        overall_idx = ((batch_idx - 1) * batch_size) + company_idx + 1
        
        log_prefix = f"[Batch {batch_idx}/{total_batches}][Company {company_idx + 1}/{batch_size}][Overall {overall_idx}]"
        logging.info(f"{log_prefix} Starting processing for '{company_name}' (TPID: {tpid})")
        
        processor = CompanyProcessor(output_folder, temp_folder)
        result = processor.process_company(row)
        processor.cleanup()
        
        success = "SUCCESS" if result[0] else "FAILED"
        source = result[1]
        logging.info(f"{log_prefix} {success}: '{company_name}' - Source: {source}")
        
        return result
        
    except Exception as e:
        logging.error(f"Error processing company {row.get('tpid', 'Unknown')}: {str(e)}")
        return False, f"Error: {str(e)}", {
            'DiscoveredURL': None,
            'FinalDomain': None,
            'LogoSource': f"Error: {str(e)}",
            'URLSource': None
        }

def process_batch(companies_df, output_folder, temp_folder, num_processes=None, batch_idx=1, total_batches=1):
    """Process a batch of companies in parallel."""
    if num_processes is None:
        # Determine number of processes based on CPU count and configured max
        num_processes = min(os.cpu_count() or 4, CONFIG['MAX_PROCESSES'])
    
    batch_size = len(companies_df)
    logging.info(f"Starting batch {batch_idx}/{total_batches} with {batch_size} companies using {num_processes} processes")
        
    try:
        # Prepare arguments for each company
        process_args = [
            (row, output_folder, temp_folder, batch_idx, total_batches, i, batch_size)
            for i, (_, row) in enumerate(companies_df.iterrows())
        ]
        
        # Run in parallel with timing
        start_time = time.monotonic()
        logging.info(f"Batch {batch_idx}/{total_batches}: Processing started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Launch worker pool
        with Pool(processes=num_processes) as pool:
            try:
                results = pool.map(process_company_wrapper, process_args)
            except KeyboardInterrupt:
                pool.terminate()
                logging.info(f"Batch {batch_idx}/{total_batches}: Processing interrupted by user")
                raise
                
        duration = time.monotonic() - start_time
        
        # Count successes and analyze sources
        successful = sum(1 for r in results if r[0])
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        # Create enriched dataframe
        enriched_df = enrich_batch_results(companies_df, results)
        
        # Get source breakdowns
        sources = {}
        for r in results:
            source = r[1]
            if source in sources:
                sources[source] += 1
            else:
                sources[source] = 1
        
        # Log detailed batch completion info
        logging.info(f"Batch {batch_idx}/{total_batches}: Completed in {duration:.2f}s")
        logging.info(f"Batch {batch_idx}/{total_batches}: Success rate: {successful}/{total} ({success_rate:.1f}%)")
        logging.info(f"Batch {batch_idx}/{total_batches}: Sources breakdown: {sources}")
        
        return successful, total, enriched_df
    except Exception as e:
        logging.error(f"Error in batch {batch_idx}/{total_batches} processing: {str(e)}")
        return 0, len(companies_df), pd.DataFrame()