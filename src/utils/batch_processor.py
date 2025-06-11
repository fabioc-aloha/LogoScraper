"""Batch Processing Module

This module handles the parallel processing of company batches for logo scraping."""

import os
import signal
import time
from multiprocessing import Pool
import pandas as pd
from src.utils.company_processor import CompanyProcessor
from src.config import CONFIG

def init_worker():
    """Initialize worker process to ignore SIGINT."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def process_company_wrapper(args):
    """Wrapper function for processing a single company in parallel."""
    row, output_folder = args
    processor = CompanyProcessor(output_folder)
    try:
        success, source = processor.process_company(row)
        return str(row['ID']), success, source
    finally:
        processor.cleanup()

def process_batch(companies_df: pd.DataFrame, output_folder: str,
                 num_processes: int = None, batch_idx: int = 1, total_batches: int = 1,
                 batch_start_times: list = None):
    """Process a batch of companies in parallel.
    
    Args:
        companies_df: DataFrame with company data
        output_folder: Where to save the logos
        num_processes: Number of parallel processes to use
        batch_idx: Current batch index
        total_batches: Total number of batches
        batch_start_times: List to track batch timings for ETA calculation
        
    Returns:
        Tuple[int, int, pd.DataFrame]: (successful_count, total_count, results_df)
    """
    batch_start_time = time.time()
    
    if num_processes is None:
        num_processes = min(os.cpu_count() - 1 or 1, CONFIG.get('MAX_PROCESSES', 8))
    
    # Prepare arguments for parallel processing
    process_args = [(row, output_folder) for _, row in companies_df.iterrows()]

    results = []
    total = len(process_args)
    success_count = 0
    fail_count = 0

    with Pool(num_processes, initializer=init_worker) as pool:
        # Instead of using tqdm for batch progress, we'll use simple print statements
        # to avoid conflicts with the main progress bar
        print(f"  Processing batch {batch_idx}/{total_batches} ({total} companies)...")
        
        for result in pool.imap_unordered(process_company_wrapper, process_args):
            results.append(result)
            _, success, _ = result
            if success:
                success_count += 1
            else:
                fail_count += 1
              # Print periodic progress updates (every 25 companies or at the end)
            completed = success_count + fail_count
            if completed % 25 == 0 or completed == total:
                rate = 100 * (success_count / completed) if completed > 0 else 0
                status_emoji = "🟩" if rate >= 90 else "🟨" if rate >= 50 else "🟥"
                print(f"    {status_emoji} Progress: {completed}/{total} ({rate:.1f}% success)")
        
        batch_end_time = time.time()
        batch_duration = batch_end_time - batch_start_time
          # Record batch timing for ETA calculation
        if batch_start_times is not None:
            batch_start_times.append(batch_duration)
        
        final_rate = 100 * (success_count / total) if total > 0 else 0
        status_emoji = "🟩" if final_rate >= 90 else "🟨" if final_rate >= 50 else "🟥"
        
        # Calculate and display ETA if we have multiple batches
        eta_message = ""
        if total_batches > 1 and batch_start_times and len(batch_start_times) > 0:
            batches_remaining = total_batches - batch_idx
            if batches_remaining > 0:
                # Calculate average batch time
                avg_batch_time = sum(batch_start_times) / len(batch_start_times)
                # Inflate ETA for first 1-2 batches
                if len(batch_start_times) == 1:
                    eta_seconds = avg_batch_time * batches_remaining * 1.5
                elif len(batch_start_times) == 2:
                    eta_seconds = avg_batch_time * batches_remaining * 1.2
                else:
                    eta_seconds = avg_batch_time * batches_remaining
                eta_message = f" | ETA: {_format_duration(eta_seconds)}"
        
        print(f"  {status_emoji} Batch {batch_idx} completed: {success_count}/{total} logos ({final_rate:.1f}% success){eta_message}")

    results_df = pd.DataFrame(
        [(id, success, source) for id, success, source in results],
        columns=['ID', 'LogoGenerated', 'LogoSource']
    )

    return success_count, total, results_df


def _format_duration(seconds: float) -> str:
    """Format time duration in a human-readable way."""
    if seconds < 0:
        return "0s"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds_remaining = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds_remaining}s"
    else:
        return f"{int(seconds)}s"