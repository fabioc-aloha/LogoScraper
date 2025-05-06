"""Batch Processing Module

This module handles the parallel processing of company batches for logo retrieval.
It manages the multiprocessing pool and coordinates the company processors.
"""

import logging
import multiprocessing as mp
from typing import Set, Dict, Any
import pandas as pd

from utils.company_processor import CompanyProcessor
from utils.progress_tracker import ProgressTracker

def process_company_wrapper(args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for processing a single company in parallel.
    
    Args:
        args: Dictionary containing:
            - row: DataFrame row with company data
            - output_folder: Directory for saving logos
            - temp_folder: Directory for temporary files
            
    Returns:
        Dictionary containing processing results
    """
    try:
        processor = CompanyProcessor(args['output_folder'], args['temp_folder'])
        success, source, enrichment_data = processor.process_company(args['row'])
        processor.cleanup()
        
        return {
            'tpid': str(args['row']['TPID']),
            'success': success,
            'source': source,
            'enrichment': enrichment_data
        }
    except Exception as e:
        logging.error(f"Error processing company {args['row']['TPID']}: {str(e)}")
        return {
            'tpid': str(args['row']['TPID']),
            'success': False,
            'source': f"Error: {str(e)}",
            'enrichment': {
                'DiscoveredURL': None,
                'FinalDomain': None,
                'LogoSource': f"Error: {str(e)}",
                'URLSource': None
            }
        }

def process_batch(df: pd.DataFrame, output_folder: str, temp_folder: str,
                 failed_domains: Set[str], total_companies: int,
                 progress_tracker: ProgressTracker) -> tuple[int, int, pd.DataFrame]:
    """Process a batch of companies in parallel.
    
    Args:
        df: DataFrame containing the batch of companies
        output_folder: Directory where processed logos will be saved
        temp_folder: Directory for temporary files during processing
        failed_domains: Set of domains that previously failed
        total_companies: Total number of companies being processed
        progress_tracker: Tracks overall processing progress
        
    Returns:
        tuple containing:
        - Number of successfully processed companies
        - Total number of companies attempted
        - DataFrame with enrichment data
    """
    # Prepare arguments for parallel processing
    process_args = []
    for _, row in df.iterrows():
        process_args.append({
            'row': row,
            'output_folder': output_folder,
            'temp_folder': temp_folder
        })
    
    # Process companies in parallel
    successful = 0
    enrichment_data = []
    
    with mp.Pool() as pool:
        results = pool.map(process_company_wrapper, process_args)
        
        # Update progress and collect enrichment data
        for result in results:
            tpid = result['tpid']
            if result['success']:
                successful += 1
                progress_tracker.mark_completed(tpid)
                logging.info(f"Successfully saved logo for TPID {tpid} from {result['source']}")
            else:
                progress_tracker.mark_failed(tpid)
                logging.error(f"Failed to process TPID {tpid}: {result['source']}")
                
            # Add enrichment data
            enrichment_data.append({
                'TPID': tpid,
                **result['enrichment']
            })
    
    # Create enrichment DataFrame
    enrichment_df = pd.DataFrame(enrichment_data)
    enriched_df = df.merge(enrichment_df, on='TPID', how='left')
    
    return successful, len(process_args), enriched_df