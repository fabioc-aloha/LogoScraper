"""Image Processing Utilities

This module serves as a facade for image processing functionality,
delegating to specialized modules.
"""

from utils.image_resizer import save_standardized_logo
from utils.default_logo_generator import create_default_logo

# Re-export core functions
__all__ = ['save_standardized_logo', 'create_default_logo']