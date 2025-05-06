from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'infra', 'infra_config.json')
with open(config_file, 'r') as f:
    config = json.load(f)

# Get storage info
storage_url = config['inputData']['storageUrl']
container_name = config['inputData']['containerName']
folder_path = config['inputData']['filePath']

logger.info(f"Storage URL: {storage_url}")
logger.info(f"Container: {container_name}")
logger.info(f"Folder path: {folder_path}")

try:
    # Initialize client
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(account_url=storage_url, credential=credential)

    # Get container client
    file_system_client = service_client.get_file_system_client(container_name)

    # List all Parquet files in the specified folder
    print(f"\nListing Parquet files in '{folder_path}':")
    print("=" * 50)

    paths = file_system_client.get_paths(path=folder_path, recursive=True)
    parquet_files = []

    for path in paths:
        logger.info(f"Found path: {path.name}")
        if path.name.endswith('.parquet'):
            print(f"Parquet file found - Path: {path.name}, Size: {path.content_length:,} bytes")
            parquet_files.append(path.name)

    if not parquet_files:
        print(f"No Parquet files found in {folder_path}")
    else:
        print(f"\nTotal Parquet files found: {len(parquet_files)}")

except Exception as e:
    logger.error(f"Error: {str(e)}")
    raise