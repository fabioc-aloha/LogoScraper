"""Global configuration for the logo scraper"""

CONFIG = {
    'OUTPUT_SIZE': 512,  # Target size for logos
    'MIN_SOURCE_SIZE': 120,  # Minimum source image size to avoid excessive upscaling
    'BATCH_SIZE': 200,  # Number of companies to process in each batch
    'OUTPUT_FOLDER': 'logos',  # Output folder for saved logos
    'TEMP_FOLDER': 'temp',  # Temporary folder for logo validation
    'INPUT_FILE': 'Companies.xlsx',  # Input Excel file containing company data
    'CORNER_RADIUS': 40  # Corner radius for rounded rectangles in default logos
}