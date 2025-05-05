"""Image Processing Utilities

This module provides comprehensive image processing functionality for the logo scraper.
It handles various image operations including:
- Logo standardization and resizing
- Text rendering for default logos
- Image format conversion
- Quality validation
- Multi-language text support
"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
from config import CONFIG

def rounded_rectangle(draw, xy, radius, fill):
    """Draw a rounded rectangle on an image.
    
    Args:
        draw (ImageDraw): The PIL drawing context
        xy (list): List of [x1, y1, x2, y2] coordinates for rectangle corners
        radius (int): Corner radius in pixels
        fill (tuple): RGB color tuple for filling the rectangle
    
    The function creates a rectangle with rounded corners by combining:
    - Main rectangle body
    - Four corner pieces using pie slices
    """
    x1, y1, x2, y2 = xy
    # Draw main rectangle
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    # Draw four corners
    draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=fill)
    draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=fill)

def create_default_logo(company_name):
    """Create a default logo for a company using their name.
    
    This function generates a visually appealing default logo when no suitable
    logo can be found online. It creates a rounded rectangle with the company
    name or initials in a professional color scheme.
    
    Args:
        company_name (str): The name of the company
    
    Returns:
        bytes or None: PNG image data if successful, None if generation fails
    
    Features:
    - Professional color palette
    - Multi-language font support (CJK + Latin)
    - Automatic text sizing and layout
    - Fallback to initials for long names
    - Multiple font fallbacks
    - Error handling and logging
    """
    try:
        size = CONFIG['OUTPUT_SIZE']
        # Create image with white background
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        
        # Professional colors (RGB tuples)
        colors = [
            (52, 152, 219),    # Blue
            (46, 204, 113),    # Green
            (155, 89, 182),    # Purple
            (52, 73, 94),      # Dark Blue
            (41, 128, 185),    # Medium Blue
            (39, 174, 96),     # Medium Green
            (142, 68, 173),    # Deep Purple
            (41, 58, 74),      # Navy Blue
            (44, 62, 80),      # Dark Navy
            (19, 106, 138),    # Ocean Blue
            (22, 160, 133),    # Teal
            (26, 188, 156),    # Turquoise
            (27, 79, 114),     # Steel Blue
            (40, 116, 166),    # Royal Blue
            (69, 179, 157),    # Sea Green
            (83, 57, 138),     # Royal Purple
            (86, 101, 115),    # Slate Gray
            (108, 52, 131),    # Deep Violet
            (125, 206, 160),   # Mint Green
            (169, 50, 38)      # Deep Red
        ]
        
        # Try fonts with good Unicode support
        font = None
        font_size = int(size * 0.4)  # Scale initial font size with image size
        try_fonts = [
            "ARIALUNI.TTF",
            "msgothic.ttc",
            "simhei.ttf",
            "malgun.ttf",
            "arialbd.ttf",
            "arial.ttf"
        ]
        
        for font_name in try_fonts:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
        
        if font is None:
            font = ImageFont.load_default()
            font_size = 30

        # Draw rounded rectangle background - no padding
        background_color = random.choice(colors)
        rounded_rectangle(draw, [0, 0, size, size], CONFIG['CORNER_RADIUS'], background_color)

        # Calculate available space inside rectangle - small margin for text
        margin = int(size * 0.04)  # Scale margin with image size
        max_text_width = size - (2 * margin)
        max_text_height = size - (2 * margin)

        # Try to fit the full company name
        words = company_name.split()
        if len(company_name) <= 15:
            # Short name - try single line
            text = company_name
            font_size = adjust_font_size(draw, text, font, max_text_width, max_text_height, start_size=int(size * 0.4), min_size=int(size * 0.06))
            if font_size:
                font = ImageFont.truetype(font.path, font_size)
                draw_centered_text(draw, text, font, size, size)
                
        elif len(words) >= 2:
            # Try up to four lines
            max_lines = 4 if len(company_name) >= 30 else (3 if len(company_name) >= 20 else 2)
            lines = split_into_lines(company_name, max_lines)
            max_line_height = max_text_height / (len(lines) * 1.2)  # Reduced line spacing multiplier
            
            # Find font size that fits all lines
            font_size = find_font_size_for_lines(draw, lines, font, max_text_width, max_line_height, start_size=int(size * 0.4), min_size=int(size * 0.06))
            if font_size:
                font = ImageFont.truetype(font.path, font_size)
                draw_multiline_text(draw, lines, font, size, size)
            else:
                # Fall back to initials if text doesn't fit
                if len(words) == 1:
                    initials = words[0][:2].upper()
                else:
                    initials = ''.join(word[0] for word in words[:3]).upper()  # Take up to 3 initials
                font_size = int(size * 0.4)
                font = ImageFont.truetype(font.path, font_size)
                draw_centered_text(draw, initials, font, size, size)
        else:
            # Fall back to first two characters for CJK text or single long word
            initials = company_name[:2].upper()
            font_size = int(size * 0.4)
            font = ImageFont.truetype(font.path, font_size)
            draw_centered_text(draw, initials, font, size, size)

        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
    except Exception as e:
        logging.error(f"Error creating default logo for {company_name}: {str(e)}")
        return None

def adjust_font_size(draw, text, font, max_width, max_height, start_size=None, min_size=None):
    """Find the largest font size that fits text within given dimensions.
    
    This function performs a binary search to find the optimal font size
    that allows the text to fit within the specified boundaries.
    
    Args:
        draw (ImageDraw): The PIL drawing context
        text (str): The text to size
        font (ImageFont): Base font to use (path will be used)
        max_width (int): Maximum allowed width in pixels
        max_height (int): Maximum allowed height in pixels
        start_size (int, optional): Starting font size to try
        min_size (int, optional): Minimum acceptable font size
    
    Returns:
        int or None: The largest font size that fits, or None if text cannot fit
    """
    # Default sizes relative to output size if not provided
    if start_size is None:
        start_size = int(CONFIG['OUTPUT_SIZE'] * 0.4)
    if min_size is None:
        min_size = int(CONFIG['OUTPUT_SIZE'] * 0.06)
        
    for size in range(start_size, min_size - 1, -4):
        test_font = ImageFont.truetype(font.path, size)
        bbox = draw.textbbox((0, 0), text, font=test_font)
        if (bbox[2] - bbox[0]) <= max_width and (bbox[3] - bbox[1]) <= max_height:
            return size
    return None

def split_into_lines(text, max_lines):
    """Split text into optimal lines for display.
    
    This function attempts to split text into roughly equal lines while
    respecting word boundaries when possible.
    
    Args:
        text (str): The text to split
        max_lines (int): Maximum number of lines to create
    
    Returns:
        list: List of strings, each representing a line of text
    
    The function balances:
    - Even distribution of characters across lines
    - Word boundary preservation
    - Maximum line count
    """
    words = text.split()
    if len(words) <= max_lines:
        return words
        
    chars_per_line = len(text) // max_lines
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) > chars_per_line and len(lines) < max_lines - 1:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
        
    return lines

def find_font_size_for_lines(draw, lines, font, max_width, max_height, start_size=None, min_size=None):
    """Find the largest font size that fits multiple lines of text.
    
    Args:
        draw (ImageDraw): The PIL drawing context
        lines (list): List of text lines to fit
        font (ImageFont): Base font to use (path will be used)
        max_width (int): Maximum allowed width in pixels
        max_height (int): Maximum allowed height in pixels
        start_size (int, optional): Starting font size to try
        min_size (int, optional): Minimum acceptable font size
    
    Returns:
        int or None: The largest font size that fits all lines, or None if
            text cannot fit
    """
    # Default sizes relative to output size if not provided
    if start_size is None:
        start_size = int(CONFIG['OUTPUT_SIZE'] * 0.4)
    if min_size is None:
        min_size = int(CONFIG['OUTPUT_SIZE'] * 0.06)
        
    for size in range(start_size, min_size - 1, -4):
        test_font = ImageFont.truetype(font.path, size)
        fits = True
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=test_font)
            if (bbox[2] - bbox[0]) > max_width or (bbox[3] - bbox[1]) > max_height:
                fits = False
                break
        if fits:
            return size
    return None

def draw_centered_text(draw, text, font, width, height):
    """Draw text centered both horizontally and vertically.
    
    This function handles proper text positioning with consideration for:
    - Font metrics (ascent/descent)
    - Visual centering adjustments
    - Pixel-perfect positioning
    
    Args:
        draw (ImageDraw): The PIL drawing context
        text (str): The text to draw
        font (ImageFont): The font to use
        width (int): Total width of the image
        height (int): Total height of the image
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    ascent, descent = font.getmetrics()
    
    x = (width - text_width) / 2
    vertical_offset = (descent - ascent) * 0.1
    y = (height - text_height) / 2 + vertical_offset
    
    draw.text((x, y), text, font=font, fill='white')

def draw_multiline_text(draw, lines, font, width, height):
    """Draw multiple lines of text with proper spacing and centering.
    
    This function handles the layout of multiple text lines with:
    - Vertical spacing between lines (18% of line height)
    - Individual line centering
    - Overall block centering
    - Visual weight balancing
    
    Args:
        draw (ImageDraw): The PIL drawing context
        lines (list): List of text lines to draw
        font (ImageFont): The font to use
        width (int): Total width of the image
        height (int): Total height of the image
    """
    # Calculate total height of all lines
    line_heights = []
    total_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        total_height += line_height
    
    # Add some spacing between lines (18% of line height)
    line_spacing = line_heights[0] * 0.18  # Increased from 0.15
    total_height += line_spacing * (len(lines) - 1)
    
    # Calculate starting Y position to center all lines vertically
    current_y = (height - total_height) / 2
    
    # Draw each line
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) / 2
        draw.text((x, current_y), line, font=font, fill='white')
        current_y += line_heights[i] + line_spacing

def save_standardized_logo(image_data, output_path):
    """Save logo as a standardized PNG with quality controls.
    
    This function processes and validates logo images, ensuring they meet
    quality standards before saving. It handles:
    - Image format conversion
    - Size standardization
    - Quality validation
    - Transparency handling
    - Error recovery
    
    Args:
        image_data (bytes): Raw image data to process
        output_path (str): Where to save the processed logo
    
    Returns:
        bool: True if processing and saving succeeded, False otherwise
    
    Quality checks:
    - Minimum source image size
    - Maximum upscaling ratio (8x)
    - Format validation
    - Output verification
    """
    if not image_data:
        return False
    
    try:
        # Verify the image data
        try:
            img = Image.open(BytesIO(image_data))
            img.load()
        except Exception as e:
            logging.error(f"Invalid image data for {output_path}: {str(e)}")
            return False
            
        # Check source image dimensions - use largest dimension
        largest_dimension = max(img.width, img.height)
        if largest_dimension < CONFIG['MIN_SOURCE_SIZE']:
            logging.error(f"Source image too small (largest dimension: {largest_dimension}px) for {output_path}")
            return False
        
        # Handle special formats
        if img.format == 'ICO':
            if hasattr(img, 'get_sizes'):
                sizes = img.get_sizes()
                if sizes:
                    largest_size = max(sizes, key=lambda t: t[0])
                    if largest_size[0] < CONFIG['MIN_SOURCE_SIZE']:
                        logging.error(f"ICO image too small: {largest_size[0]}x{largest_size[0]}")
                        return False
                    img.size = largest_size[0]
                    img.load()
        
        # Convert to RGB
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, 'white')
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            try:
                img = img.convert('RGB')
            except Exception as e:
                logging.error(f"Failed to convert image mode {img.mode} to RGB for {output_path}: {str(e)}")
                return False

        # Create new image with white background
        new_img = Image.new('RGB', (CONFIG['OUTPUT_SIZE'], CONFIG['OUTPUT_SIZE']), 'white')
        
        # Calculate resize dimensions
        ratio = min(CONFIG['OUTPUT_SIZE'] / img.width, CONFIG['OUTPUT_SIZE'] / img.height)
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        
        # Check if upscaling ratio is too high (original is too small)
        if ratio > 8:  # If we need to upscale more than 8x
            logging.error(f"Image requires too much upscaling ({ratio:.1f}x) for {output_path}")
            return False
        
        try:
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception as e:
            logging.error(f"Failed to resize image: {str(e)}")
            return False
        
        # Center the image
        x = (CONFIG['OUTPUT_SIZE'] - new_width) // 2
        y = (CONFIG['OUTPUT_SIZE'] - new_height) // 2
        
        new_img.paste(img, (x, y))
        
        # Save as PNG
        try:
            new_img.save(output_path, 'PNG', quality=95, optimize=True)
            
            # Verify the saved file
            with Image.open(output_path) as verify_img:
                verify_img.verify()
            
            return True
        except Exception as e:
            logging.error(f"Failed to save or verify image: {str(e)}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            return False
            
    except Exception as e:
        logging.error(f"Error saving logo: {str(e)}")
        return False