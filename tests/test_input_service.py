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

if __name__ == "__main__":
    try:
        service = InputDataService()
        df = service.get_data()
        
        print("\nOriginal vs Lowercase Column Names:")
        original_df = pd.read_excel(CONFIG['INPUT_FILE'])
        print("Original columns:")
        for col in original_df.columns:
            print(f"  {col}")
        
        print("\nAfter lowercase conversion:")
        for col in df.columns:
            print(f"  {col}")
            
        # Display sample values for key columns
        key_columns = ['tpid', 'tpname', 'websiteurl']
        print("\nSample values for key columns (first row):")
        for col in key_columns:
            if col in df.columns:
                print(f"{col}: {df[col].iloc[0]}")
            else:
                print(f"{col}: Not found in file")
                
        # Display URL-related columns
        print("\nAll URL-related columns:")
        url_columns = [col for col in df.columns if 'url' in col.lower()]
        for col in url_columns:
            non_null = df[col].count()
            total = len(df)
            percentage = (non_null / total) * 100
            print(f"{col}: {non_null}/{total} filled ({percentage:.1f}%)")
            
        # Display name-related columns
        print("\nAll name-related columns:")
        name_columns = [col for col in df.columns if 'name' in col.lower()]
        for col in name_columns:
            non_null = df[col].count()
            total = len(df)
            percentage = (non_null / total) * 100
            print(f"{col}: {non_null}/{total} filled ({percentage:.1f}%)")
            
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        sys.exit(1)