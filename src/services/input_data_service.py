"""Input Data Service

This module handles reading and filtering data from Excel files.
Simplified to focus on core functionality.
"""

import logging
import os
import pandas as pd
from src.config import CONFIG

class InputDataService:
    """Service for handling input data from Excel files."""

    def get_data(self, filters=None, top_n=None):
        """Get filtered data from input file (CSV or Excel).
        
        Expected input columns: ID, CompanyName, WebsiteURL, Country.
        """
        try:
            file_path = CONFIG['INPUT_FILE']
            if not os.path.exists(file_path):
                logging.error(f"Input file not found: {file_path}")
                return pd.DataFrame()

            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Check for required input columns
            required_input_columns = ['ID', 'CompanyName', 'WebsiteURL', 'Country']
            for col in required_input_columns:
                if col not in df.columns:
                    logging.error(f"Required column '{col}' not found in input file")
                    return pd.DataFrame()

            # Clean data but keep the new column names
            df['ID'] = df['ID'].astype(str)
            df['CompanyName'] = df['CompanyName'].fillna('')
            df['WebsiteURL'] = df['WebsiteURL'].fillna('')
            df['Country'] = df['Country'].fillna('')

            # Remove rows with missing required data
            valid_rows = df['CompanyName'].str.strip() != ''
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