"""Input Data Service

This module handles fetching and filtering data from Azure Data Lake Storage Gen2.
It supports reading Parquet datasets and applying filters before processing.
"""

import os
import io
import json
import logging
import pandas as pd
import pyarrow.parquet as pq
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import sys

# Add parent directory to Python path to import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CONFIG

class InputDataService:
    """Service for handling input data from Azure Data Lake Storage Gen2."""
    
    def __init__(self, config_file=None):
        """Initialize the input data service."""
        try:
            # Configure logging
            if CONFIG.get('HIDE_AUTH_LOGS'):
                logging.getLogger('azure.identity').setLevel(logging.WARNING)
                logging.getLogger('azure.core.pipeline.policies').setLevel(logging.WARNING)
            
            # Load configuration
            if config_file is None:
                config_file = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'infra',
                    'infra_config.json'
                )
            
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Config file not found: {config_file}")
                
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            
            # Validate input data configuration
            input_config = self.config.get('inputData', {})
            required_fields = ['storageUrl', 'containerName', 'filePath']
            missing_fields = [f for f in required_fields if not input_config.get(f)]
            if missing_fields:
                raise ValueError(
                    f"Missing required input data configuration: {', '.join(missing_fields)}"
                )
            
            # Initialize Data Lake client
            self.storage_url = input_config['storageUrl']
            self.container_name = input_config['containerName']
            self.file_pattern = input_config['filePath']
            
            if input_config.get('useManagedIdentity', True):
                credential = DefaultAzureCredential()
            else:
                raise ValueError("Only managed identity authentication is supported")
                
            self.datalake_client = DataLakeServiceClient(
                account_url=self.storage_url,
                credential=credential
            )
            
        except Exception as e:
            logging.error(f"Error initializing InputDataService: {str(e)}")
            raise

    def list_available_columns(self):
        """Get list of available columns in the dataset."""
        try:
            # Get the first dataset to check columns
            df = self.get_data(top_n=1)
            columns = list(df.columns)
            logging.debug(f"Available columns: {', '.join(columns)}")
            return columns
        except Exception as e:
            logging.error(f"Error listing columns: {str(e)}")
            return []

    def get_data(self, filters=None, top_n=None):
        """Get filtered data from Azure Data Lake Storage."""
        try:
            # Get container client
            file_system_client = self.datalake_client.get_file_system_client(self.container_name)
            
            # If pattern ends with *.parquet, get all matching files in directory
            if '*' in self.file_pattern:
                directory = os.path.dirname(self.file_pattern)
                paths = file_system_client.get_paths(path=directory)
                files = [path.name for path in paths if path.name.endswith('.parquet')]
            else:
                # Single file case
                files = [self.file_pattern]
            
            if not files:
                raise ValueError(f"No Parquet files found matching {self.file_pattern}")
            
            dfs = []
            total_rows = 0
            
            for file_path in files:
                logging.debug(f"Reading file: {file_path}")
                file_client = file_system_client.get_file_client(file_path)
                download = file_client.download_file()
                df = pq.read_table(io.BytesIO(download.readall())).to_pandas()
                
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
                
                dfs.append(df)
                total_rows += len(df)
                logging.debug(f"Read {len(df):,} rows from {file_path}")
                
                # Check if we've reached top_n
                if top_n and total_rows >= top_n:
                    # Trim the last dataframe if needed
                    last_df = dfs[-1]
                    rows_needed = top_n - (total_rows - len(last_df))
                    dfs[-1] = last_df.head(rows_needed)
                    break
            
            # Combine all dataframes
            final_df = pd.concat(dfs, ignore_index=True)
            
            # Apply top_n limit if still needed (in case of filtering)
            if top_n and len(final_df) > top_n:
                final_df = final_df.head(top_n)
            
            logging.info(f"Retrieved {len(final_df):,} rows")
            
            return final_df
            
        except Exception as e:
            logging.error(f"Error getting data: {str(e)}")
            raise