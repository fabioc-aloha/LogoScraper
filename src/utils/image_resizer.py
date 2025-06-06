"""Image Resizing Module

This module handles image resizing and standardization functionality.

Recent changes:
- The minimum source size check now requires at least one dimension (width or height) to be >= MIN_SOURCE_SIZE, not both.
- The upscaling ratio limit has been removed; upscaling is only limited by the configured output dimensions.
"""

import logging
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from src.config import CONFIG

# Custom Exceptions
class ImageProcessingError(Exception):
    """Base class for image processing errors."""
    pass

class InvalidImageDataError(ImageProcessingError):
    """Error for invalid or unidentifiable image data."""
    pass

class ImageTooSmallError(ImageProcessingError):
    """Error for images that are too small to process."""
    pass

class ImageConversionError(ImageProcessingError):
    """Error during image mode conversion (e.g., to RGB)."""
    pass

class ImageResizingError(ImageProcessingError):
    """Error during the resize or standardization process."""
    pass

class ImageSaveError(ImageProcessingError):
    """Error during image saving or verification."""
    pass


def save_standardized_logo(image_data, output_path):
    """
    Save logo as a standardized PNG with quality controls.
    Raises ImageProcessingError or its subclasses on failure.
    """
    if not image_data:
        raise InvalidImageDataError(f"No image data provided for {output_path}")
    
    # No top-level try-except here; specific exceptions from helpers will propagate.
    # Logging of these errors will be handled by the caller (e.g., CompanyProcessor)
    img = validate_and_load_image(image_data, output_path)
    img = convert_to_rgb(img, output_path)
    new_img = create_standardized_image(img, output_path)
    save_final_image(new_img, output_path)
    # If all steps succeed, implicitly returns None, indicating success.
    # The caller should check for exceptions to determine failure.

def validate_and_load_image(image_data, output_path):
    """
    Validate and load the image data.
    Raises InvalidImageDataError or ImageTooSmallError on failure.
    At least one dimension (width or height) must be >= MIN_SOURCE_SIZE.
    """
    try:
        img = Image.open(BytesIO(image_data))
        img.load() # Ensure image data is loaded
    except UnidentifiedImageError as e:
        raise InvalidImageDataError(f"Cannot identify image file for {output_path}: {str(e)}") from e
    except Exception as e: # Catch other PIL errors
        raise InvalidImageDataError(f"Invalid image data for {output_path}: {str(e)}") from e

    # Check source image dimensions
    min_source_size = CONFIG.get('MIN_SOURCE_SIZE', 50) # Default if not in config
    if img.width < min_source_size and img.height < min_source_size:
        raise ImageTooSmallError(
            f"Source image for {output_path} is too small ({img.width}x{img.height}). "
            f"Both width and height are below minimum {min_source_size}px."
        )
        
    # Handle ICO format specifically for size checks
    if img.format == 'ICO':
        # For ICO, Pillow loads the best available size by default with img.load()
        # We re-check the loaded image's size.
        if img.width < min_source_size and img.height < min_source_size:
            try:
                if hasattr(img, '_ico'):
                    sizes = img._ico.sizes()
                    if sizes:
                        largest_ico_size = max(sizes, key=lambda t: t[0])
                        if largest_ico_size[0] >= min_source_size or largest_ico_size[1] >= min_source_size:
                            pass # Acceptable size exists
                        else:
                            raise ImageTooSmallError(
                                f"ICO image {output_path} best size ({img.width}x{img.height}) is below minimum {min_source_size}px. "
                                f"Largest internal ICO size also too small: {largest_ico_size[0]}x{largest_ico_size[1]}px."
                            )
            except Exception as e:
                logging.debug(f"Could not further interrogate ICO sizes for {output_path}: {e}")
                if img.width < min_source_size and img.height < min_source_size:
                    raise ImageTooSmallError(
                        f"ICO image {output_path} ({img.width}x{img.height}) is below minimum {min_source_size}px after initial load."
                    )
    return img

def convert_to_rgb(img, output_path):
    """
    Convert image to RGB format.
    Raises ImageConversionError on failure.
    """
    try:
        if img.mode == 'RGBA':
            # Create a white background for transparency
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the RGBA image onto the white background using the alpha channel as mask
            background.paste(img, mask=img.split()[3]) 
            return background
        elif img.mode != 'RGB':
            return img.convert('RGB')
        return img # Already RGB
    except Exception as e:
        raise ImageConversionError(f"Failed to convert image mode '{img.mode}' to RGB for {output_path}: {str(e)}") from e

def create_standardized_image(img, output_path):
    """
    Create a standardized size image with consistent dimensions and quality.
    
    This algorithm implements several key image processing techniques:
    - Aspect ratio preservation - Maintains the original image proportions
    - White background standardization - Ensures consistency across all outputs
    - Anti-aliased resizing - Uses LANCZOS resampling for highest quality downsampling
    - Centered positioning - Places the image in the center of the standardized canvas
    - Upscaling prevention - (Removed: now upscaling is only limited by configured dimensions)
    
    Args:
        img: PIL Image object to standardize.
        output_path: Path where the image will be saved (for logging purposes).
        
    Returns:
        PIL Image: A new standardized image.
    Raises:
        ImageResizingError: If processing failed, e.g., due to Pillow errors.
    """
    output_size = CONFIG.get('OUTPUT_SIZE', 256) # Default if not in config
    try:
        # Create new image with white background
        new_img = Image.new('RGB', (output_size, output_size), (255, 255, 255))
        
        # Calculate resize dimensions
        ratio = min(output_size / img.width, output_size / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        
        # Remove upscaling ratio check: allow any upscaling as per user config
        # Resize and center image using high-quality downsampling
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        x_offset = (output_size - new_width) // 2
        y_offset = (output_size - new_height) // 2
        new_img.paste(resized_img, (x_offset, y_offset))
        
        return new_img
        
    except Exception as e:
        # Catch any other Pillow-related errors during resizing or pasting
        raise ImageResizingError(f"Failed to standardize image for {output_path}: {str(e)}") from e

def save_final_image(img, output_path):
    """
    Save the final image and verify it.
    Raises ImageSaveError on failure.
    """
    try:
        # Save with high quality and optimization for PNG
        img.save(output_path, 'PNG', quality=CONFIG.get('PNG_QUALITY', 95), optimize=True)
        
        # Verify the saved file can be opened and is a valid image
        with Image.open(output_path) as verify_img:
            verify_img.verify() # Verifies image integrity
            # Optionally, check if it's actually a PNG
            if verify_img.format != 'PNG':
                raise ImageSaveError(f"Verification failed for {output_path}: Saved file is not PNG (format: {verify_img.format})")

    except Exception as e:
        raise ImageSaveError(f"Failed to save or verify image at {output_path}: {str(e)}") from e