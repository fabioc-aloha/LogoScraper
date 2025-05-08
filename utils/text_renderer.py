"""Text Rendering Module

This module handles text rendering functionality for logo generation with comprehensive 
multilingual support for all writing systems and languages.
"""

import logging
import os
import platform
import unicodedata
from PIL import ImageFont, Image, ImageDraw
from config import CONFIG

# Define universal fonts that work well for multi-language support
FONT_PRIORITIES = {
    'Windows': [
        # Universal coverage fonts first
        "arialuni.ttf",      # Arial Unicode MS (excellent universal coverage)
        "seguisym.ttf",      # Segoe UI Symbol (good Unicode support)
        
        # Fonts with broad language support
        "malgun.ttf",        # Malgun Gothic (Korean)
        "meiryo.ttc",        # Meiryo (Japanese)
        "msyh.ttf",          # Microsoft YaHei (Chinese)
        "tahoma.ttf",        # Excellent for Latin, Cyrillic, Arabic, Thai, Vietnamese
        "gulim.ttc",         # Good for Korean
        "segoeui.ttf",       # Good multilingual support
        "arial.ttf",         # Good for Latin, Cyrillic, Greek
        "times.ttf",         # Times New Roman
        "simsun.ttc",        # SimSun (Chinese)
        "simhei.ttf",        # SimHei (Chinese)
        "mingliu.ttc",       # MingLiu (Traditional Chinese)
        "msgothic.ttc",      # MS Gothic (Japanese)
        "batang.ttc",        # Batang (Korean)
        "aparaj.ttf",        # Aparajita (Devanagari)
        "nirmala.ttf",       # Nirmala UI (Indian scripts)
        "ebrima.ttf",        # Ebrima (African scripts)
        "gadugi.ttf",        # Gadugi (Cherokee and other American scripts)
        "mvboli.ttf",        # MV Boli (Persian)
        "sylfaen.ttf",       # Sylfaen (Armenian, Georgian)
        "leelawad.ttf",      # Leelawadee (Thai)
        "calibri.ttf",       # Calibri (good general support)
        "cambria.ttc",       # Cambria (good general support)
        "verdana.ttf",       # Verdana
        "georgia.ttf",       # Georgia
    ],
    'Darwin': [  # macOS
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/PingFang.ttc",           # Chinese
        "/System/Library/Fonts/Hiragino Sans GB.ttc",   # Chinese
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",   # Korean
        "/System/Library/Fonts/HiraginoSans.ttc",       # Japanese
        "/System/Library/Fonts/AppleGothic.ttf",        # Multilingual
        "/System/Library/Fonts/STHeiti Light.ttc",      # Chinese
        "/System/Library/Fonts/Menlo.ttc",              # Monospace multilingual
        "/System/Library/Fonts/Thonburi.ttc",           # Thai
        "/System/Library/Fonts/Kannada Sangam MN.ttc",  # Kannada
        "/System/Library/Fonts/Gurmukhi MN.ttc",        # Gurmukhi
        "/System/Library/Fonts/Khmer Sangam MN.ttc",    # Khmer
        "/System/Library/Fonts/Arial.ttf",              # Good for Latin, Cyrillic
        "/System/Library/Fonts/Times New Roman.ttf",    # Latin, Cyrillic support
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/LucidaGrande.ttc"
    ],
    'Linux': [
        # Universal coverage fonts
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        
        # Language specific fonts
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansTibetan-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansKhmer-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf",
        
        # Fallbacks
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
}

# Script-specific fonts for better rendering
SCRIPT_SPECIFIC_FONTS = {
    'cyrillic': [
        "arial.ttf",       # Arial has good Cyrillic coverage
        "tahoma.ttf",      # Tahoma has excellent Cyrillic support
        "verdana.ttf",     # Verdana has good Cyrillic support
        "georgia.ttf",     # Georgia 
        "times.ttf",       # Times New Roman
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'cjk': [
        "malgun.ttf",      # Malgun Gothic (Korean) - prioritized for Korean
        "msyh.ttf",        # Microsoft YaHei (Chinese)
        "meiryo.ttc",      # Meiryo (Japanese)
        "msgothic.ttc",    # MS Gothic (Japanese)
        "simhei.ttf",      # SimHei (Chinese)
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'arabic': [
        "arial.ttf",       # Arial has decent Arabic support
        "tahoma.ttf",      # Good Arabic support
        "segoeui.ttf",     # Segoe UI
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'devanagari': [
        "mangal.ttf",      # Mangal (Hindi)
        "aparajita.ttf",   # Aparajita
        "kokila.ttf",      # Kokila
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'thai': [
        "cordia.ttc",      # Cordia New
        "angsana.ttc",     # AngsanaUPC
        "tahoma.ttf",      # Tahoma has good Thai support
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'hebrew': [
        "david.ttf",       # David
        "arial.ttf",       # Arial has good Hebrew support
        "tahoma.ttf",      # Tahoma 
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'greek': [
        "arial.ttf",       # Arial has good Greek support
        "tahoma.ttf",      # Tahoma
        "times.ttf",       # Times New Roman
        "arialuni.ttf",    # Arial Unicode (fallback)
    ],
    'turkish': [
        "tahoma.ttf",      # Tahoma has excellent Turkish support
        "arial.ttf",       # Arial has good Turkish support
        "verdana.ttf",     # Good Turkish support
        "calibri.ttf",     # Good Turkish support
        "segoeui.ttf",     # Segoe UI
        "arialuni.ttf",    # Arial Unicode MS (fallback)
    ],
}

# Additional fonts paths - exact paths to preferred fonts for problematic scripts
SPECIAL_FONT_PATHS = {
    'turkish': {
        'Windows': [
            'C:\\Windows\\Fonts\\tahoma.ttf',  # Best for Turkish
            'C:\\Windows\\Fonts\\arial.ttf',   # Good alternative
        ]
    },
    'korean': {
        'Windows': [
            'C:\\Windows\\Fonts\\malgun.ttf',  # Best for Korean
            'C:\\Windows\\Fonts\\gulim.ttc',   # Another Korean font
        ]
    }
}

def get_system_font_directory():
    """Get the system font directory based on the operating system."""
    system = platform.system()
    if system == 'Windows':
        return os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
    elif system == 'Darwin':  # macOS
        return '/System/Library/Fonts'
    elif system == 'Linux':
        # Common font directories in Linux
        candidates = [
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            os.path.expanduser('~/.fonts')
        ]
        for path in candidates:
            if os.path.isdir(path):
                return path
        return '/usr/share/fonts'  # Default fallback
    else:
        return None

def detect_script(text):
    """
    Detect the dominant script used in a text to optimize font selection.
    Returns: 'cyrillic', 'cjk', 'latin', 'arabic', 'devanagari', 'thai', 'hebrew', 'greek', 'turkish', 'korean', or 'other'
    """
    if not text:
        return 'latin'
        
    # Count characters by script
    counts = {
        'cyrillic': 0,
        'korean': 0,  # Separate Korean from other CJK
        'cjk': 0,
        'latin': 0,
        'arabic': 0,
        'devanagari': 0,
        'thai': 0, 
        'hebrew': 0,
        'greek': 0,
        'turkish': 0,
        'other': 0
    }
    
    # Turkish-specific characters
    turkish_chars = set('ıİğĞüÜşŞöÖçÇ')
    
    for char in text:
        # Skip whitespace and punctuation
        if char.isspace() or unicodedata.category(char).startswith('P'):
            continue
        
        # Check for Turkish special characters
        if char in turkish_chars:
            counts['turkish'] += 1
            continue
            
        # Get character name and category
        try:
            name = unicodedata.name(char, '').upper()
            category = unicodedata.category(char)
        except ValueError:
            # If we can't get the Unicode name, consider it 'other'
            counts['other'] += 1
            continue
        
        # Identify script
        if 'HANGUL' in name:
            counts['korean'] += 1
        elif any(script in name for script in ('CJK', 'HIRAGANA', 'KATAKANA', 'BOPOMOFO')):
            counts['cjk'] += 1
        elif 'CYRILLIC' in name:
            counts['cyrillic'] += 1
        elif 'LATIN' in name or char.isascii():
            counts['latin'] += 1
        elif 'ARABIC' in name:
            counts['arabic'] += 1
        elif 'DEVANAGARI' in name:
            counts['devanagari'] += 1
        elif 'THAI' in name:
            counts['thai'] += 1
        elif 'HEBREW' in name:
            counts['hebrew'] += 1
        elif 'GREEK' in name:
            counts['greek'] += 1
        else:
            counts['other'] += 1
    
    # Determine dominant script
    total = sum(counts.values())
    if total == 0:
        return 'latin'
    
    # Special case handling for Korean
    if counts['korean'] > 0:
        return 'korean'
    
    # Special case for Turkish: even just a few Turkish characters means we should use Turkish
    if counts['turkish'] > 1:
        return 'turkish'
        
    # Find script with most characters
    dominant_script = max(counts.items(), key=lambda x: x[1])
    script_name, count = dominant_script
    
    # If more than 20% characters are of a non-Latin script, use that script
    if script_name != 'latin' and count / total > 0.2:
        return script_name
    # If more than 60% characters are Latin, treat as Latin
    elif counts['latin'] / total > 0.6:
        return 'latin'
    else:
        return 'other'

def get_font(size, try_fonts=None):
    """Get a font of the specified size with support for international characters."""
    system = platform.system()
    
    # Use system-specific font list if no fonts are specified
    if try_fonts is None:
        try_fonts = FONT_PRIORITIES.get(system, FONT_PRIORITIES['Windows'])
    
    # Get system font directory
    fonts_dir = get_system_font_directory()
    
    # Try each font in the priority list
    for font_name in try_fonts:
        # Determine full path for relative font names
        if os.path.isabs(font_name) or os.path.isfile(font_name):
            font_path = font_name
        else:
            font_path = os.path.join(fonts_dir, font_name)
        
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            logging.debug(f"Could not load font {font_name}: {str(e)}")
            continue
    
    # As a last resort, try to use system default fonts through PIL
    try:
        default_font = ImageFont.load_default()
        logging.warning("Using PIL default font; some characters may not render correctly")
        return default_font
    except Exception as e:
        logging.error(f"Failed to load any usable font: {str(e)}")
        
    # Ultimate fallback - try to create a basic font
    logging.error("No suitable font found for text rendering")
    return None

def get_script_specific_font(script, size):
    """Get a font that's optimized for a specific script."""
    if script in SCRIPT_SPECIFIC_FONTS:
        # Try script-specific fonts first
        font = get_font(size, SCRIPT_SPECIFIC_FONTS[script])
        if font:
            return font
    
    # Fall back to general font selection if we couldn't find a script-specific font
    return get_font(size)

def load_font_with_fallback(script, size):
    """Load a font with special handling for problematic scripts like Turkish and Korean"""
    system = platform.system()
    
    # Try to load a specific font for problematic scripts
    if script in SPECIAL_FONT_PATHS and system in SPECIAL_FONT_PATHS[script]:
        for font_path in SPECIAL_FONT_PATHS[script][system]:
            try:
                if os.path.exists(font_path):
                    logging.info(f"Loading specialized font for {script}: {font_path}")
                    return ImageFont.truetype(font_path, size)
            except Exception as e:
                logging.debug(f"Failed to load specialized font {font_path}: {str(e)}")
    
    # Fall back to regular font loading
    return get_script_specific_font(script, size)

def adjust_font_size(draw, text, font, max_width, max_height, start_size=None, min_size=None):
    """Find the largest font size that fits text within given dimensions."""
    if start_size is None:
        start_size = int(CONFIG['OUTPUT_SIZE'] * 0.4)
    if min_size is None:
        min_size = int(CONFIG['OUTPUT_SIZE'] * 0.06)
    
    # If the font failed to load, try to get a font that works
    if font is None:
        for test_size in range(start_size, min_size - 1, -4):
            test_font = get_font(test_size)
            if test_font:
                font = test_font
                break
        # If we still don't have a font, give up
        if font is None:
            return None
        
    for size in range(start_size, min_size - 1, -4):
        try:
            # Get font path safely
            font_path = getattr(font, "path", None)
            if font_path:
                test_font = ImageFont.truetype(font_path, size)
            else:
                # If no path, try to get a new font at this size
                test_font = get_font(size)
                if not test_font:
                    continue
                    
            # Get text size with this font
            bbox = draw.textbbox((0, 0), text, font=test_font)
            if (bbox[2] - bbox[0]) <= max_width and (bbox[3] - bbox[1]) <= max_height:
                return size
        except Exception as e:
            logging.debug(f"Error when testing font size {size}: {str(e)}")
            continue
            
    return None

def split_into_lines(text, max_lines):
    """Split text into optimal lines for display."""
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
    """Find the largest font size that fits multiple lines of text."""
    if start_size is None:
        start_size = int(CONFIG['OUTPUT_SIZE'] * 0.4)
    if min_size is None:
        min_size = int(CONFIG['OUTPUT_SIZE'] * 0.06)
        
    for size in range(start_size, min_size - 1, -4):
        try:
            font_path = getattr(font, "path", None)
            if font_path:
                test_font = ImageFont.truetype(font_path, size)
                
                fits = True
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=test_font)
                    if (bbox[2] - bbox[0]) > max_width:
                        fits = False
                        break
                        
                # Check total height
                if fits:
                    total_height = 0
                    for line in lines:
                        bbox = draw.textbbox((0, 0), line, font=test_font)
                        total_height += (bbox[3] - bbox[1])
                    
                    # Add spacing between lines (15% of font height)
                    line_spacing = test_font.getmetrics()[0] * 0.15
                    total_height += line_spacing * (len(lines) - 1)
                    
                    if total_height <= max_height:
                        return size
            else:
                # If no path attribute, try different approach
                test_font = get_font(size)
                if not test_font:
                    continue
                
                # Test with this font
                return find_font_size_for_lines(draw, lines, test_font, max_width, max_height, size, min_size)
                
        except Exception as e:
            logging.debug(f"Error when testing font size {size} for multiple lines: {str(e)}")
            continue
            
    return None

def draw_centered_text(draw, text, font, width, height):
    """Draw text centered both horizontally and vertically, with a slight upward adjustment."""
    try:
        # Try using textbbox first which is more accurate
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center horizontally
        x = (width - text_width) / 2
        
        # Position vertically - move text up by adjusting vertical position
        vertical_adjustment = height * 0.07  # Positive value moves text up
        y = (height - text_height) / 2 - vertical_adjustment
        
        draw.text((x, y), text, font=font, fill='white')
    except Exception as e:
        logging.warning(f"Error using textbbox for text centering: {str(e)}")
        try:
            # Fallback to older method that works with all PIL versions
            font_metrics = font.getmetrics()
            ascent, descent = font_metrics
            
            # Estimate text size using getsize if available
            if hasattr(font, "getsize"):
                text_width, text_height = font.getsize(text)
            else:
                # Very rough estimation
                text_width = len(text) * (font.size // 2)
                text_height = font.size
                
            x = (width - text_width) / 2
            y = (height - text_height) / 2 - height * 0.07  # 7% upward adjustment
            
            draw.text((x, y), text, font=font, fill='white')
        except Exception as e2:
            logging.error(f"Text rendering fallback also failed: {str(e2)}")
            # Last resort - use anchor="mm" for middle-middle if supported
            try:
                draw.text((width/2, height/2), text, font=font, fill='white', anchor="mm")
            except:
                # Very basic fallback without positioning
                draw.text((10, height/2), text, font=font, fill='white')

def draw_multiline_text(draw, lines, font, width, height):
    """Draw multiple lines of text with proper spacing and centering, with a slight upward adjustment."""
    try:
        # Calculate heights
        line_heights = []
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            total_height += line_height
        
        # Add line spacing (15% of line height for better spacing with more lines)
        line_spacing = line_heights[0] * 0.15
        total_height += line_spacing * (len(lines) - 1)
        
        # Draw lines - with a 7% upward adjustment
        vertical_adjustment = height * 0.07  # Positive value moves text up
        current_y = (height - total_height) / 2 - vertical_adjustment
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            draw.text((x, current_y), line, font=font, fill='white')
            current_y += line_heights[i] + line_spacing
    except Exception as e:
        logging.warning(f"Error in multiline text rendering: {str(e)}")
        try:
            # Fallback approach - calculate positions manually
            font_metrics = font.getmetrics()
            line_height = font_metrics[0] + font_metrics[1]  # ascent + descent
            line_spacing = line_height * 0.15
            total_height = line_height * len(lines) + line_spacing * (len(lines) - 1)
            
            current_y = (height - total_height) / 2 - height * 0.07  # 7% upward adjustment
            
            for line in lines:
                # Estimate text width
                if hasattr(font, "getsize"):
                    text_width, _ = font.getsize(line)
                else:
                    text_width = len(line) * (font.size // 2)  # Rough estimate
                    
                x = (width - text_width) / 2
                draw.text((x, current_y), line, font=font, fill='white')
                current_y += line_height + line_spacing
        except Exception as e2:
            logging.error(f"Multiline text fallback rendering also failed: {str(e2)}")
            # Last resort - join lines and use simple centered text
            try:
                combined_text = "\n".join(lines)
                draw.text((width/2, height/2), combined_text, font=font, fill='white', anchor="mm")
            except:
                # Very basic fallback
                y = height/3
                for line in lines:
                    draw.text((10, y), line, font=font, fill='white')
                    y += font.size * 1.5

# ... keep other existing functions ...