"""Image Resizing Module

This module handles image resizing and standardization functionality.
"""

import logging
from io import BytesIO
from PIL import Image
from config import CONFIG

def save_standardized_logo(image_data, output_path):
    """Save logo as a standardized PNG with quality controls."""
    if not image_data:
        return False
    
    try:
        img = validate_and_load_image(image_data, output_path)
        if not img:
            return False
            
        img = convert_to_rgb(img, output_path)
        if not img:
            return False
            
        new_img = create_standardized_image(img, output_path)
        if not new_img:
            return False
            
        return save_final_image(new_img, output_path)
            
    except Exception as e:
        logging.error(f"Error saving logo: {str(e)}")
        return False

def validate_and_load_image(image_data, output_path):
    """Validate and load the image data."""
    try:
        img = Image.open(BytesIO(image_data))
        img.load()
        
        # Check source image dimensions
        largest_dimension = max(img.width, img.height)
        if largest_dimension < CONFIG['MIN_SOURCE_SIZE']:
            logging.warning(f"Source image too small (largest dimension: {largest_dimension}px) for {output_path}")
            return None
            
        # Handle ICO format
        if img.format == 'ICO' and hasattr(img, 'get_sizes'):
            sizes = img.get_sizes()
            if sizes:
                largest_size = max(sizes, key=lambda t: t[0])
                if largest_size[0] < CONFIG['MIN_SOURCE_SIZE']:
                    logging.warning(f"ICO image too small: {largest_size[0]}x{largest_size[0]}")
                    return None
                img.size = largest_size[0]
                img.load()
                
        return img
        
    except Exception as e:
        logging.error(f"Invalid image data for {output_path}: {str(e)}")
        return None

def convert_to_rgb(img, output_path):
    """Convert image to RGB format."""
    try:
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, 'white')
            background.paste(img, mask=img.split()[3])
            return background
        elif img.mode != 'RGB':
            return img.convert('RGB')
        return img
    except Exception as e:
        logging.error(f"Failed to convert image mode {img.mode} to RGB for {output_path}: {str(e)}")
        return None

def create_standardized_image(img, output_path):
    """
    Create a standardized size image with consistent dimensions and quality.
    
    This algorithm implements several key image processing techniques:
    1. Aspect ratio preservation - Maintains the original image proportions
    2. White background standardization - Ensures consistency across all outputs
    3. Anti-aliased resizing - Uses LANCZOS resampling for highest quality downsampling
    4. Centered positioning - Places the image in the center of the standardized canvas
    5. Upscaling prevention - Rejects images requiring excessive upscaling (>8x) which
       would result in poor quality outputs
    
    Args:
        img: PIL Image object to standardize
        output_path: Path where the image will be saved (for logging purposes)
        
    Returns:
        PIL Image: A new standardized image, or None if processing failed
    """
    try:
        # Create new image with white background
        new_img = Image.new('RGB', (CONFIG['OUTPUT_SIZE'], CONFIG['OUTPUT_SIZE']), 'white')
        
        # Calculate resize dimensions
        ratio = min(CONFIG['OUTPUT_SIZE'] / img.width, CONFIG['OUTPUT_SIZE'] / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        
        # Check upscaling ratio
        if ratio > 8:
            logging.error(f"Image requires too much upscaling ({ratio:.1f}x) for {output_path}")
            return None
            
        # Resize and center image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        x = (CONFIG['OUTPUT_SIZE'] - new_width) // 2
        y = (CONFIG['OUTPUT_SIZE'] - new_height) // 2
        new_img.paste(img, (x, y))
        
        return new_img
        
    except Exception as e:
        logging.error(f"Failed to standardize image: {str(e)}")
        return None

def save_final_image(img, output_path):
    """Save the final image and verify it."""
    try:
        img.save(output_path, 'PNG', quality=95, optimize=True)
        
        # Verify the saved file
        with Image.open(output_path) as verify_img:
            verify_img.verify()
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to save or verify image: {str(e)}")
        return False