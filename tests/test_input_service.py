"""Test script for InputDataService to display company data sample"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Add the parent directory to sys.path to import from services
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

from services.input_data_service import InputDataService
from config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format for cleaner output
)

# Hide authentication logs
logging.getLogger('azure.identity').setLevel(logging.ERROR)
logging.getLogger('azure.core.pipeline.policies').setLevel(logging.ERROR)

# Configure pandas display
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)
pd.set_option('display.max_colwidth', 25)
pd.set_option('display.show_dimensions', True)

def format_df(df):
    """Format dataframe for display"""
    # Use display columns from config
    cols = [col for col in CONFIG['DISPLAY_COLUMNS'] if col in df.columns]
    preview = df[cols].copy()
    
    # Truncate long strings for better display
    for col in preview.columns:
        if preview[col].dtype == 'object':
            preview[col] = preview[col].fillna('').astype(str).str.slice(0, 25)
    
    return preview

if __name__ == "__main__":
    try:
        service = InputDataService()
        print(f"Fetching data (top_n={CONFIG['TOP_N']}) with filters: {CONFIG['FILTERS']}")
        df = service.get_data(filters=CONFIG['FILTERS'], top_n=CONFIG['TOP_N'])
        
        print(f"\nRetrieved {len(df):,} rows")
        print("\nSample data (configured columns only):")
        display_df = format_df(df)
        print(display_df.to_string())
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)