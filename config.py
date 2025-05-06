"""Global Configuration for Logo Scraper

This module provides centralized configuration for the logo scraper application.
All configurable parameters are defined here to allow easy customization.
"""

CONFIG = {
    # Output and Processing
    'OUTPUT_SIZE': 512,  # Target size (width and height) in pixels for all processed logos
    'MIN_SOURCE_SIZE': 120,  # Minimum source image dimension in pixels to avoid quality loss
    'BATCH_SIZE': 200,  # Number of companies to process in each parallel batch
    'TOP_N': 50,  # Limit number of companies to process
    'OUTPUT_FOLDER': 'logos',  # Directory where processed logos are saved
    'TEMP_FOLDER': 'temp',  # Directory for temporary files during processing
    'INPUT_FILE': 'Companies.xlsx',  # Excel file containing company data
    'CORNER_RADIUS': 40,  # Corner radius in pixels for default logo rounded rectangles

    # Azure Configuration
    'AZURE_CONFIG_FILE': 'azure_config.json',  # Azure configuration file path
    'MIN_LOGO_QUALITY': 0.5,  # Minimum quality score (0-1) for logos from Azure Vision
    'ENABLE_BRAND_DETECTION': True,  # Whether to use Azure Vision brand detection
    'ENABLE_INAPPROPRIATE_CHECK': True,  # Whether to check for inappropriate content
    'USE_CDN_URLS': True,  # Whether to use CDN URLs in output data

    # Logging Configuration
    'LOG_LEVEL': 'INFO',  # Logging level (DEBUG, INFO, WARNING, ERROR)
    'LOG_FORMAT': '%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    'HIDE_AUTH_LOGS': True,  # Hide authentication and request logging

    # Display Configuration
    'DISPLAY_COLUMNS': [
        'tpid',
        'mssalesaccountname',
        'segment',
        'industry',
        'country',
        'city'
    ],

    # Available Filter Columns (organized by category)
    'FILTER_COLUMNS': {
        # Core Identifiers
        'IDENTIFIERS': [
            'tpid',                     # Trading Partner ID (e.g., '8546275')
            'AccountId',                # Global Account ID (GUID)
            'crmid',                    # CRM Account ID
            'mssalesid',                # MS Sales ID
            'jarvisaccountcid',         # Jarvis Account ID
            'dunsnumber',               # DUNS Number
        ],

        # Company Names and Translation
        'NAMES': [
            'tpname',                   # Trading Partner Name
            'mssalesaccountname',       # MS Sales Account Name
            'crmaccountname',           # CRM Account Name
            'tpidaccountenglishname',   # English Account Name
            'tpidlocalname',           # Local Language Name
            'translatedaccountname',    # Translated Account Name
        ],

        # Location Information
        'LOCATION': [
            'country',                  # Country Name
            'countryid',               # Country ID
            'city',                    # City Name
            'stateorprovince',         # State/Province
            'postalcode',              # Postal Code
            'addressline1',            # Address Line 1
            'addressline2',            # Address Line 2
        ],

        # Contact Information
        'CONTACT': [
            'websiteurl',              # Website URL
            'mainphone',               # Main Phone Number
            'fax',                     # Fax Number
        ],

        # Business Segmentation
        'SEGMENTATION': [
            'segment',                 # Segment (e.g., 'Strategic Commercial')
            'segmentid',              # Segment ID
            'subsegment',             # Subsegment
            'subsegmentid',           # Subsegment ID
            'segmentgroup',           # Segment Group (e.g., 'SMB')
            'summarysegmentname',     # Summary Segment Name
            'industry',               # Industry
            'vertical',               # Vertical
            'subvertical',           # Subvertical
            'verticalcategory',       # Vertical Category
            'sector',                 # Sector
        ],

        # Geographic Organization
        'GEOGRAPHY': [
            'fieldarea',              # Field Area
            'fieldregion',            # Field Region
            'fieldsubregion',         # Field Subregion
            'fieldsubsidiary',        # Field Subsidiary
            'bigareaname',            # Big Area Name
            'areaname',               # Area Name
            'regionname',             # Region Name
            'subregionname',          # Subregion Name
        ],

        # Account Status and Type
        'STATUS': [
            'accountstatus',          # Account Status
            'status',                 # Status
            'accounttype',            # Account Type
            'organizationtypename',   # Organization Type
            'customertype',           # Customer Type
            'parentinglevel',         # Parenting Level
        ],

        # Sales Organization
        'SALES': [
            'salesgroup',             # Sales Group
            'salesunit',              # Sales Unit
            'salesterritory',         # Sales Territory
            'accountexecutive',       # Account Executive
            'am',                     # Account Manager
            'amfullname',             # Account Manager Full Name
        ],

        # Cloud and Services
        'CLOUD_SERVICES': [
            'azure_penetration',      # Azure Penetration
            'cloudacquisitionazureflag',  # Cloud Acquisition Azure Flag
            'cloudacquisitionmwflag',  # Cloud Acquisition Modern Workplace Flag
            'cloudacquisitionbizappsflag',  # Cloud Acquisition Business Apps Flag
        ],

        # Metadata
        'METADATA': [
            'createdon',              # Created Date
            'createdby',             # Created By
            'lastmodifieddate',       # Last Modified Date
            'lastupdateddate',        # Last Updated Date
            'source',                 # Source System
        ]
    },

    # Filtering Configuration (uncomment and modify filters as needed)
    'FILTERS': {
        'parentinglevel': 'Top Parent',
        'status': 'Active'
    },

    # Service Rate Limits (requests per minute)
    'CLEARBIT_RATE_LIMIT': 3600,     # 60 requests per second for Clearbit API
    'DUCKDUCKGO_RATE_LIMIT': 1800,   # 30 requests per second for DuckDuckGo service
    'AZURE_VISION_RATE_LIMIT': 600,  # 10 requests per second for Azure Vision API

    # HTTP Configuration
    'REQUEST_TIMEOUT': 10,  # Timeout in seconds for HTTP requests
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}