"""Azure Storage Service Integration

This module provides integration with Azure Blob Storage for storing and serving
logos through Azure CDN.
"""

import os
import sys
import json
import logging
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

class AzureStorageService:
    """Service class for Azure Blob Storage integration.
    
    This class manages logo storage in Azure Blob Storage and integrates
    with Azure CDN for efficient delivery.
    
    Args:
        config_file (str, optional): Path to Azure configuration file.
            If not provided, will look for azure_config.json in root directory.
    
    Attributes:
        blob_service_client (BlobServiceClient): Azure Blob Storage client
        credential (DefaultAzureCredential): Azure credential for authentication
        cdn_endpoint (str): The CDN endpoint URL for serving logos
    """

    def __init__(self, config_file=None):
        """Initialize the Azure Storage service."""
        try:
            # Load Azure configuration
            if config_file is None:
                config_file = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'azure_config.json'
                )
            
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"Azure config file not found: {config_file}")
                
            with open(config_file, 'r') as f:
                self.azure_config = json.load(f)
            
            # Set up authentication using managed identity
            self.credential = DefaultAzureCredential()
            
            # Initialize Blob Storage client
            account_url = f"https://{self.azure_config['STORAGE_ACCOUNT_NAME']}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=self.credential
            )
            
            # Store CDN endpoint
            self.cdn_endpoint = self.azure_config['CDN_ENDPOINT'].rstrip('/')
            
        except Exception as e:
            logging.error(f"Error initializing Azure Storage service: {str(e)}")
            raise

    def save_logo(self, tpid, image_data):
        """Save a logo to Azure Blob Storage.
        
        Args:
            tpid (str): The TPID identifier for the logo
            image_data (bytes): The logo image data to save
            
        Returns:
            str: The CDN URL where the logo can be accessed, or None if failed
        """
        try:
            # Get container client
            container_client = self.blob_service_client.get_container_client('logos')
            
            # Upload with proper content type
            blob_name = f"{tpid}.png"
            blob_client = container_client.get_blob_client(blob_name)
            
            blob_client.upload_blob(
                image_data,
                overwrite=True,
                content_settings=ContentSettings(
                    content_type='image/png',
                    cache_control='public, max-age=31536000'  # Cache for 1 year
                )
            )
            
            # Return CDN URL
            return f"{self.cdn_endpoint}/logos/{blob_name}"
            
        except Exception as e:
            logging.error(f"Error saving logo for TPID {tpid}: {str(e)}")
            return None

    def save_temp_file(self, filename, data):
        """Save a temporary file to Azure Blob Storage.
        
        Args:
            filename (str): Name for the temporary file
            data (bytes): File data to save
            
        Returns:
            str: The URL where the temp file can be accessed, or None if failed
        """
        try:
            # Get container client
            container_client = self.blob_service_client.get_container_client('temp')
            
            # Upload file
            blob_client = container_client.get_blob_client(filename)
            content_type = 'application/octet-stream'
            if filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith('.json'):
                content_type = 'application/json'
            
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(
                    content_type=content_type,
                    cache_control='no-cache'  # Don't cache temp files
                )
            )
            
            return blob_client.url
            
        except Exception as e:
            logging.error(f"Error saving temp file {filename}: {str(e)}")
            return None

    def delete_temp_file(self, filename):
        """Delete a temporary file from Azure Blob Storage.
        
        Args:
            filename (str): Name of the temporary file to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            container_client = self.blob_service_client.get_container_client('temp')
            blob_client = container_client.get_blob_client(filename)
            blob_client.delete_blob()
            return True
        except Exception as e:
            logging.error(f"Error deleting temp file {filename}: {str(e)}")
            return False

    def get_logo_url(self, tpid):
        """Get the CDN URL for a logo.
        
        Args:
            tpid (str): The TPID identifier for the logo
            
        Returns:
            str: The CDN URL where the logo can be accessed
        """
        return f"{self.cdn_endpoint}/logos/{tpid}.png"