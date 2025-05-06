"""DataFrame Filtering Utilities

This module provides functionality for filtering pandas DataFrames based on
configuration settings. It supports exact matches and wildcard patterns for
flexible filtering of company data.
"""

import logging
import pandas as pd
from config import CONFIG

def apply_filters(df):
    """Apply configured filters to the DataFrame.
    
    This method filters the DataFrame based on the FILTERS configuration.
    Supports both exact matches and wildcards (* character).
    
    Args:
        df (pandas.DataFrame): DataFrame to filter
    
    Returns:
        pandas.DataFrame: Filtered DataFrame
    
    Examples:
        With CONFIG['FILTERS'] set to:
        {
            'Industry': ['Technology', 'Healthcare'],
            'Region': 'EMEA*',
            'Status': '*Active*'
        }
        It will:
        1. Match Industry exactly against Technology OR Healthcare
        2. Match Region starting with EMEA
        3. Match Status containing Active anywhere
    """
    if not CONFIG.get('FILTERS'):
        return df
        
    filtered_df = df.copy()
    
    # Convert all relevant columns to string type for consistent matching
    for column in CONFIG['FILTERS'].keys():
        if column in filtered_df.columns:
            filtered_df[column] = filtered_df[column].astype(str)
    
    # Apply each filter
    mask = None
    for column, pattern in CONFIG['FILTERS'].items():
        if column not in filtered_df.columns:
            logging.warning(f"Filter column '{column}' not found in Excel file")
            continue
            
        current_mask = None
        
        # Handle list of patterns
        if isinstance(pattern, list):
            current_mask = filtered_df[column].isin(pattern)
        else:
            # Handle wildcard patterns
            if isinstance(pattern, str):
                if pattern.startswith('*') and pattern.endswith('*'):
                    # Contains pattern
                    search_pattern = pattern.strip('*')
                    current_mask = filtered_df[column].str.contains(search_pattern, na=False)
                elif pattern.startswith('*'):
                    # Ends with pattern
                    search_pattern = pattern.lstrip('*')
                    current_mask = filtered_df[column].str.endswith(search_pattern)
                elif pattern.endswith('*'):
                    # Starts with pattern
                    search_pattern = pattern.rstrip('*')
                    current_mask = filtered_df[column].str.startswith(search_pattern)
                else:
                    # Exact match
                    current_mask = filtered_df[column] == pattern
        
        if current_mask is not None:
            if mask is None:
                mask = current_mask
            else:
                # Always combine with AND
                mask = mask & current_mask
    
    if mask is not None:
        filtered_df = filtered_df[mask]
        
    return filtered_df