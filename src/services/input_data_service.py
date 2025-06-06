"""Input Data Service

This module handles reading and filtering data from Excel files.
Simplified to focus on core functionality.
"""

import logging
import pandas as pd
from src.config import CONFIG

class InputDataService:
    """Service for handling input data from Excel files."""

    def get_data(self, filters=None, top_n=None):
        """Get filtered data from Excel file."""
        try:
            # Read Excel file
            input_file = CONFIG['INPUT_FILE']
            logging.debug(f"Reading file: {input_file}")
            df = pd.read_excel(input_file)
            
            # Convert all column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Validate required columns
            required_columns = ['tpid', 'crmaccountname']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Required columns missing from input file: {', '.join(missing_columns)}")
            
            # Ensure websiteurl and country columns exist (optional fields)
            if 'websiteurl' not in df.columns:
                df['websiteurl'] = None
                logging.warning("websiteurl column not found in input file")
            if 'country' not in df.columns:
                df['country'] = None
                logging.warning("country column not found in input file")
            
            # Clean data
            df['tpid'] = df['tpid'].astype(str)
            df['crmaccountname'] = df['crmaccountname'].fillna('')
            df['websiteurl'] = df['websiteurl'].fillna('')
            df['country'] = df['country'].fillna('')
            
            # Remove rows with missing required data
            valid_rows = df['crmaccountname'].str.strip() != ''
            if not valid_rows.all():
                invalid_count = (~valid_rows).sum()
                logging.warning(f"Removing {invalid_count} rows with missing company names")
                df = df[valid_rows]
            
            # Convert filters to lowercase if provided
            if filters:
                filters = {k.lower(): v for k, v in filters.items()}
                
            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    if column not in df.columns:
                        logging.warning(f"Filter column '{column}' not found")
                        continue
                        
                    if isinstance(value, list):
                        df = df[df[column].isin(value)]
                    else:
                        df = df[df[column] == value]
            
            # Apply top_n limit if provided
            if top_n:
                df = df.head(top_n)
            
            logging.info(f"Retrieved {len(df):,} rows")
            return df
            
        except Exception as e:
            logging.error(f"Error getting data: {str(e)}")
            raise