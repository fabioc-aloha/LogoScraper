"""Default Logo Generator Module

This module handles the generation of default logos when no logo can be found online.
Includes support for international characters and different writing systems.
"""

import logging
import random
import unicodedata
from io import BytesIO
from PIL import Image, ImageDraw
from src.utils.text_renderer import (
    adjust_font_size, split_into_lines, 
    find_font_size_for_lines, draw_centered_text, draw_multiline_text,
    detect_script, load_font_with_fallback
)
from src.config import CONFIG

# def rounded_rectangle(draw, xy, radius, fill):
#     """Draw a rounded rectangle."""
#     x1, y1, x2, y2 = xy
#     # Draw main rectangle
#     draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
#     draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
#     # Draw corners
#     draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=fill)
#     draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=fill)
#     draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=fill)
#     draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=fill)

def get_background_color():
    """Get a professional background color."""
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
    ]
    return random.choice(colors)

def has_wide_chars(text):
    """Check if text contains any fullwidth or wide characters"""
    return any(unicodedata.east_asian_width(c) in ('W','F') for c in text)

def create_default_logo(company_name):
    """Create a default logo for a company using their name."""
    if not company_name:
        return None

    try:
        size = CONFIG['OUTPUT_SIZE']
        # Create base image
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Detect script to optimize font and layout
        script = detect_script(company_name)
        logging.info(f"Detected script for '{company_name}': {script}")
        
        # Get initial font with script-specific optimization using our enhanced font loading
        font_size = int(size * 0.4)
        font = load_font_with_fallback(script, font_size)
        
        if not font:
            logging.error(f"No suitable font found for script: {script}")
            return None

        # Draw background
        background_color = get_background_color()
        draw.rectangle([0, 0, size, size], fill=background_color)

        # Calculate text area
        margin = int(size * 0.04)
        max_text_width = size - (2 * margin)
        max_text_height = size - (2 * margin)

        # Simplified universal logic for all scripts
        # First try to fit the full company name on one line
        font_size = adjust_font_size(draw, company_name, font, max_text_width, max_text_height)
        
        if font_size:
            # Success - can fit on one line
            font = load_font_with_fallback(script, font_size)
            draw_centered_text(draw, company_name, font, size, size)
        else:
            # Need multiple lines or abbreviation
            words = company_name.split()
            
            # For scripts that don't use spaces (like CJK) or mixed double-byte chars, split by characters
            mixed_wide = has_wide_chars(company_name)
            if script in ['cjk', 'korean', 'chinese', 'japanese', 'thai'] or len(words) <= 1 or mixed_wide:
                chars = list(company_name)
                
                # Determine optimal characters per line based on total length
                if len(chars) <= 8:
                    max_chars_per_line = min(4, len(chars))
                else:
                    max_chars_per_line = min(5, max(3, len(chars) // 3))
                
                # Create lines with appropriate character grouping
                lines = []
                for i in range(0, len(chars), max_chars_per_line):
                    lines.append(''.join(chars[i:i + max_chars_per_line]))
                
                # Limit to 4 lines maximum
                lines = lines[:4]
            else:
                # For other scripts, split by words
                # Dynamically determine optimal line count based on text length
                if len(company_name) <= 20:
                    max_lines = 2
                elif len(company_name) <= 40:
                    max_lines = 3
                else:
                    max_lines = 4
                
                lines = split_into_lines(company_name, max_lines)
            
            # Calculate appropriate font size for the lines
            max_line_height = max_text_height / (len(lines) * 1.2)
            line_font_size = find_font_size_for_lines(draw, lines, font, max_text_width, max_line_height)
            
            if line_font_size:
                # Successfully fit text on multiple lines
                font = load_font_with_fallback(script, line_font_size)
                draw_multiline_text(draw, lines, font, size, size)
            else:
                # If we can't fit the text even with multiple lines, use abbreviation
                if script in ['cjk', 'korean', 'chinese', 'japanese', 'thai']:
                    # For CJK scripts, use first character or two
                    abbrev = company_name[:min(2, len(company_name))]
                else:
                    # For other scripts, try to use initials if there are multiple words
                    if len(words) > 1:
                        # Get first letter of each word, up to 4
                        abbrev = ''.join(word[0] for word in words[:min(4, len(words))]).upper()
                    else:
                        # Single word - use first up to 4 characters
                        abbrev = company_name[:min(4, len(company_name))].upper()
                
                # Apply the abbreviated text
                abbrev_font = load_font_with_fallback(script, int(size * 0.35))
                draw_centered_text(draw, abbrev, abbrev_font, size, size)

        # Draw border
        draw.rectangle([0, 0, size - 1, size - 1], outline=(0, 0, 0, 255), width=2)

        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()

    except Exception as e:
        logging.error(f"Error creating default logo for {company_name}: {str(e)}")
        return None