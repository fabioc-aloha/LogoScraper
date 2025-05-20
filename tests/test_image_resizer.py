import unittest
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# Add project root to sys.path to allow importing utils
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import image_resizer
from utils.image_resizer import (
    ImageProcessingError,
    InvalidImageDataError,
    ImageTooSmallError,
    ImageConversionError,
    ImageResizingError,
    ImageSaveError
)

# Default mock config values
MOCK_CONFIG_VALUES = {
    'MIN_SOURCE_SIZE': 50,
    'OUTPUT_SIZE': 256,
    'MAX_UPSCALING_RATIO': 8,
    'PNG_QUALITY': 95
}

class TestImageResizer(unittest.TestCase):

    def setUp(self):
        # Create a default mock image that can be configured by tests
        self.mock_image = MagicMock(spec=Image.Image)
        self.mock_image.width = 100
        self.mock_image.height = 100
        self.mock_image.format = 'PNG'
        self.mock_image.mode = 'RGB'
        # Ensure load() is a callable MagicMock
        self.mock_image.load = MagicMock()
        # Ensure convert() returns a new mock image by default
        self.mock_image.convert = MagicMock(return_value=MagicMock(spec=Image.Image, mode='RGB'))
        # Ensure resize() returns a new mock image by default
        self.mock_image.resize = MagicMock(return_value=MagicMock(spec=Image.Image))
        # Ensure split() returns a tuple of mocks (for RGBA)
        self.mock_image.split = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock(), MagicMock()))


    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.open')
    def test_validate_invalid_image_data_unidentified(self, mock_pil_image_open):
        """Test validate_and_load_image raises InvalidImageDataError for UnidentifiedImageError."""
        mock_pil_image_open.side_effect = UnidentifiedImageError("Cannot identify image")
        with self.assertRaisesRegex(InvalidImageDataError, "Cannot identify image file for output.png: Cannot identify image"):
            image_resizer.validate_and_load_image(b"bad_data", "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.open')
    def test_validate_invalid_image_data_general_pil_error(self, mock_pil_image_open):
        """Test validate_and_load_image raises InvalidImageDataError for general PIL errors."""
        mock_pil_image_open.side_effect = IOError("PIL broke") # Example of another PIL error
        with self.assertRaisesRegex(InvalidImageDataError, "Invalid image data for output.png: PIL broke"):
            image_resizer.validate_and_load_image(b"bad_data", "output.png")

    @patch.dict(image_resizer.CONFIG, {'MIN_SOURCE_SIZE': 100}, clear=True)
    @patch('PIL.Image.open')
    def test_validate_image_too_small(self, mock_pil_image_open):
        """Test validate_and_load_image raises ImageTooSmallError for small images."""
        self.mock_image.width = 50
        self.mock_image.height = 50
        mock_pil_image_open.return_value = self.mock_image
        with self.assertRaisesRegex(ImageTooSmallError, "Source image for output.png is too small \(50x50\). Largest dimension 50px < minimum 100px."):
            image_resizer.validate_and_load_image(b"dummy_data", "output.png")

    @patch.dict(image_resizer.CONFIG, {'MIN_SOURCE_SIZE': 100}, clear=True)
    @patch('PIL.Image.open')
    def test_validate_ico_image_too_small_initial_load(self, mock_pil_image_open):
        """Test ImageTooSmallError for ICO if initially loaded frame is too small."""
        self.mock_image.width = 40
        self.mock_image.height = 40
        self.mock_image.format = 'ICO'
        # Mock _ico attribute and sizes method
        self.mock_image._ico = MagicMock()
        self.mock_image._ico.sizes = MagicMock(return_value=[(32,32), (40,40)]) # No larger sizes available
        mock_pil_image_open.return_value = self.mock_image
        
        with self.assertRaisesRegex(ImageTooSmallError, "ICO image output.png best size \(40x40\) is below minimum 100px. Largest internal ICO size also too small: 40x40px."):
            image_resizer.validate_and_load_image(b"dummy_ico_data", "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.open')
    def test_validate_valid_image(self, mock_pil_image_open):
        """Test validate_and_load_image with a valid image."""
        mock_pil_image_open.return_value = self.mock_image
        img = image_resizer.validate_and_load_image(b"valid_data", "output.png")
        self.assertEqual(img, self.mock_image)
        self.mock_image.load.assert_called_once()

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.new')
    def test_convert_rgba_to_rgb(self, mock_pil_image_new):
        """Test convert_to_rgb for RGBA images."""
        self.mock_image.mode = 'RGBA'
        mock_background = MagicMock(spec=Image.Image)
        mock_pil_image_new.return_value = mock_background
        
        converted_img = image_resizer.convert_to_rgb(self.mock_image, "output.png")
        
        mock_pil_image_new.assert_called_once_with('RGB', self.mock_image.size, (255, 255, 255))
        self.mock_image.split.assert_called_once()
        mock_background.paste.assert_called_once_with(self.mock_image, mask=self.mock_image.split.return_value[3])
        self.assertEqual(converted_img, mock_background)

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    def test_convert_non_rgb_to_rgb(self):
        """Test convert_to_rgb for non-RGB/RGBA images (e.g., Palette mode)."""
        self.mock_image.mode = 'P' # Palette mode
        mock_converted_image = MagicMock(spec=Image.Image, mode='RGB')
        self.mock_image.convert = MagicMock(return_value=mock_converted_image) # Re-mock convert for this test
        
        converted_img = image_resizer.convert_to_rgb(self.mock_image, "output.png")
        self.mock_image.convert.assert_called_once_with('RGB')
        self.assertEqual(converted_img, mock_converted_image)

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    def test_convert_rgb_no_change(self):
        """Test convert_to_rgb for an image already in RGB mode."""
        self.mock_image.mode = 'RGB'
        self.mock_image.convert = MagicMock() # Re-mock to check it's NOT called
        
        converted_img = image_resizer.convert_to_rgb(self.mock_image, "output.png")
        self.mock_image.convert.assert_not_called()
        self.assertEqual(converted_img, self.mock_image)

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    def test_convert_conversion_error(self):
        """Test convert_to_rgb raises ImageConversionError if conversion fails."""
        self.mock_image.mode = 'P'
        self.mock_image.convert = MagicMock(side_effect=Exception("Conversion failed"))
        with self.assertRaisesRegex(ImageConversionError, "Failed to convert image mode 'P' to RGB for output.png: Conversion failed"):
            image_resizer.convert_to_rgb(self.mock_image, "output.png")

    @patch.dict(image_resizer.CONFIG, {'OUTPUT_SIZE': 100, 'MAX_UPSCALING_RATIO': 2}, clear=True)
    def test_create_standardized_upscaling_too_high(self):
        """Test create_standardized_image raises ImageResizingError for excessive upscaling."""
        self.mock_image.width = 10
        self.mock_image.height = 10
        # output_size (100) / img.width (10) = 10x upscaling, MAX_UPSCALING_RATIO is 2
        with self.assertRaisesRegex(ImageResizingError, "Image output.png requires too much upscaling \(10.0x\)."):
            image_resizer.create_standardized_image(self.mock_image, "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.new')
    def test_create_standardized_resize_error(self, mock_pil_image_new):
        """Test create_standardized_image raises ImageResizingError if resize fails."""
        mock_pil_image_new.return_value = MagicMock(spec=Image.Image)
        self.mock_image.resize = MagicMock(side_effect=Exception("Resize failed"))
        with self.assertRaisesRegex(ImageResizingError, "Failed to standardize image for output.png: Resize failed"):
            image_resizer.create_standardized_image(self.mock_image, "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.new')
    def test_create_standardized_success(self, mock_pil_image_new):
        """Test successful standardization path in create_standardized_image."""
        mock_canvas = MagicMock(spec=Image.Image)
        mock_pil_image_new.return_value = mock_canvas
        
        self.mock_image.width = 150
        self.mock_image.height = 100
        
        # Expected calculations for OUTPUT_SIZE = 256
        # ratio = min(256/150, 256/100) = min(1.706, 2.56) = 1.706
        # new_width = int(150 * 1.706) = int(255.9) = 255 (approx, depends on float precision)
        # new_height = int(100 * 1.706) = int(170.6) = 170 (approx)
        # For exact values, let Pillow do the math with the ratio from config
        ratio = min(MOCK_CONFIG_VALUES['OUTPUT_SIZE'] / self.mock_image.width, MOCK_CONFIG_VALUES['OUTPUT_SIZE'] / self.mock_image.height)
        expected_new_width = int(self.mock_image.width * ratio)
        expected_new_height = int(self.mock_image.height * ratio)
        expected_x_offset = (MOCK_CONFIG_VALUES['OUTPUT_SIZE'] - expected_new_width) // 2
        expected_y_offset = (MOCK_CONFIG_VALUES['OUTPUT_SIZE'] - expected_new_height) // 2

        resized_img = MagicMock(spec=Image.Image)
        self.mock_image.resize.return_value = resized_img

        result_img = image_resizer.create_standardized_image(self.mock_image, "output.png")

        mock_pil_image_new.assert_called_once_with('RGB', (MOCK_CONFIG_VALUES['OUTPUT_SIZE'], MOCK_CONFIG_VALUES['OUTPUT_SIZE']), (255, 255, 255))
        self.mock_image.resize.assert_called_once_with((expected_new_width, expected_new_height), Image.Resampling.LANCZOS)
        mock_canvas.paste.assert_called_once_with(resized_img, (expected_x_offset, expected_y_offset))
        self.assertEqual(result_img, mock_canvas)

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    def test_save_final_image_save_error(self):
        """Test save_final_image raises ImageSaveError if img.save fails."""
        self.mock_image.save = MagicMock(side_effect=Exception("Save failed"))
        with self.assertRaisesRegex(ImageSaveError, "Failed to save or verify image at output.png: Save failed"):
            image_resizer.save_final_image(self.mock_image, "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.open')
    def test_save_final_image_verify_error(self, mock_pil_image_open_verify):
        """Test save_final_image raises ImageSaveError if verification (Image.open) fails."""
        self.mock_image.save = MagicMock() # Successful save
        mock_pil_image_open_verify.side_effect = Exception("Verify open failed")
        with self.assertRaisesRegex(ImageSaveError, "Failed to save or verify image at output.png: Verify open failed"):
            image_resizer.save_final_image(self.mock_image, "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.open')
    def test_save_final_image_verify_wrong_format(self, mock_pil_image_open_verify):
        """Test save_final_image raises ImageSaveError if saved image is not PNG."""
        self.mock_image.save = MagicMock()
        mock_verified_image = MagicMock(spec=Image.Image)
        mock_verified_image.format = 'JPEG' # Not PNG
        mock_verified_image.verify = MagicMock()
        mock_pil_image_open_verify.return_value.__enter__.return_value = mock_verified_image # For 'with Image.open...'

        with self.assertRaisesRegex(ImageSaveError, "Verification failed for output.png: Saved file is not PNG \(format: JPEG\)"):
            image_resizer.save_final_image(self.mock_image, "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('PIL.Image.open')
    def test_save_final_image_success(self, mock_pil_image_open_verify):
        """Test successful save_final_image."""
        self.mock_image.save = MagicMock()
        mock_verified_image = MagicMock(spec=Image.Image)
        mock_verified_image.format = 'PNG'
        mock_verified_image.verify = MagicMock()
        mock_pil_image_open_verify.return_value.__enter__.return_value = mock_verified_image

        image_resizer.save_final_image(self.mock_image, "output.png")
        self.mock_image.save.assert_called_once_with("output.png", 'PNG', quality=MOCK_CONFIG_VALUES['PNG_QUALITY'], optimize=True)
        mock_pil_image_open_verify.assert_called_once_with("output.png")
        mock_verified_image.verify.assert_called_once()

    # Tests for save_standardized_logo (orchestrator function)
    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    def test_save_standardized_logo_no_data(self):
        """Test save_standardized_logo raises InvalidImageDataError if no image_data."""
        with self.assertRaisesRegex(InvalidImageDataError, "No image data provided for output.png"):
            image_resizer.save_standardized_logo(None, "output.png")

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('utils.image_resizer.validate_and_load_image')
    @patch('utils.image_resizer.convert_to_rgb')
    @patch('utils.image_resizer.create_standardized_image')
    @patch('utils.image_resizer.save_final_image')
    def test_save_standardized_logo_success_flow(
        self, mock_save_final, mock_create_standardized, mock_convert_rgb, mock_validate_load
    ):
        """Test the successful orchestration flow of save_standardized_logo."""
        mock_loaded_img = MagicMock(name="loaded_img")
        mock_rgb_img = MagicMock(name="rgb_img")
        mock_standardized_img = MagicMock(name="standardized_img")

        mock_validate_load.return_value = mock_loaded_img
        mock_convert_rgb.return_value = mock_rgb_img
        mock_create_standardized.return_value = mock_standardized_img
        
        image_data = b"dummy_image_data"
        output_path = "output.png"
        
        image_resizer.save_standardized_logo(image_data, output_path)
        
        mock_validate_load.assert_called_once_with(image_data, output_path)
        mock_convert_rgb.assert_called_once_with(mock_loaded_img, output_path)
        mock_create_standardized.assert_called_once_with(mock_rgb_img, output_path)
        mock_save_final.assert_called_once_with(mock_standardized_img, output_path)

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('utils.image_resizer.validate_and_load_image', side_effect=ImageTooSmallError("Too small"))
    def test_save_standardized_logo_handles_validate_error(self, mock_validate_load):
        """Test save_standardized_logo propagates error from validate_and_load_image."""
        with self.assertRaises(ImageTooSmallError):
            image_resizer.save_standardized_logo(b"data", "path.png")
        mock_validate_load.assert_called_once()

    @patch.dict(image_resizer.CONFIG, MOCK_CONFIG_VALUES, clear=True)
    @patch('utils.image_resizer.validate_and_load_image') # Returns successfully
    @patch('utils.image_resizer.convert_to_rgb', side_effect=ImageConversionError("Conversion failed"))
    def test_save_standardized_logo_handles_convert_error(self, mock_convert_rgb, mock_validate_load):
        """Test save_standardized_logo propagates error from convert_to_rgb."""
        mock_validate_load.return_value = self.mock_image # mock validate returns successfully
        with self.assertRaises(ImageConversionError):
            image_resizer.save_standardized_logo(b"data", "path.png")
        mock_validate_load.assert_called_once()
        mock_convert_rgb.assert_called_once()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Example of how to run this test file:
# python -m unittest tests.test_image_resizer
