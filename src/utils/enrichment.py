"""Data Enrichment Module

This module handles data enrichment for processed companies.
"""

import pandas as pd
from typing import List, Dict

def enrich_batch_results(companies_df: pd.DataFrame, results: List) -> pd.DataFrame:
    """Create enriched DataFrame from batch processing results.
    
    Args:
        companies_df: Original DataFrame with company data
        results: List of (success, source, data) tuples from processing
        
    Returns:
        DataFrame with enriched data
    """
    enriched_data = []
    
    # Process each result with its corresponding company data
    for (success, source, data), (_, row) in zip(results, companies_df.iterrows()):
        entry = row.to_dict()
        entry.update(data)
        entry['LogoGenerated'] = success
        entry['LogoSource'] = source
        enriched_data.append(entry)
        
    return pd.DataFrame(enriched_data)