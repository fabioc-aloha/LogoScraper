"""DataFrame Filtering Utilities

This module provides functionality for filtering pandas DataFrames based on
configuration settings. Simplified to focus on basic filtering functionality.
"""

import logging
from src.config import CONFIG

def apply_filters(df):
    """Apply configured filters to the DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame to filter
    
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    if not CONFIG.get('filters'):
        return df
        
    filtered_df = df.copy()
    
    # Ensure all filter keys are lowercase to match DataFrame columns
    filters = {k.lower(): v for k, v in CONFIG['filters'].items()}
    
    # Convert relevant columns to string type
    for column in filters.keys():
        if column in filtered_df.columns:
            filtered_df[column] = filtered_df[column].astype(str)
    
    # Apply each filter
    for column, value in filters.items():
        if column not in filtered_df.columns:
            logging.warning(f"Filter column '{column}' not found in Excel file")
            continue
            
        if isinstance(value, list):
            filtered_df = filtered_df[filtered_df[column].isin(value)]
        else:
            filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df