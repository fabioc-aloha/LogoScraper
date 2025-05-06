"""Azure Computer Vision Service Integration

This module provides integration with Azure Computer Vision for enhanced logo analysis,
including brand detection, quality assessment, and duplicate detection.
"""

import os
import sys
import json
import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.identity import DefaultAzureCredential
from msrest.authentication import CognitiveServicesCredentials

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG

class AzureVisionService:
    """Service class for Azure Computer Vision integration.
    
    This class provides enhanced logo analysis capabilities using Azure's
    Computer Vision service, including brand detection and quality assessment.
    
    Args:
        config_file (str, optional): Path to Azure configuration file.
            If not provided, will look for azure_config.json in root directory.
    
    Attributes:
        client (ComputerVisionClient): Azure Computer Vision client
        credential (DefaultAzureCredential): Azure credential for authentication
    """

    def __init__(self, config_file=None):
        """Initialize the Azure Computer Vision service."""
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
            
            # Initialize Computer Vision client
            self.client = ComputerVisionClient(
                endpoint=self.azure_config['COMPUTER_VISION_ENDPOINT'],
                credentials=self.credential
            )
            
        except Exception as e:
            logging.error(f"Error initializing Azure Vision service: {str(e)}")
            raise

    def analyze_logo(self, image_data):
        """Analyze a logo using Azure Computer Vision.
        
        This method performs comprehensive logo analysis including:
        - Brand detection
        - Quality assessment
        - Adult/racy content detection
        - Text detection
        - Object detection
        
        Args:
            image_data (bytes): Raw image data to analyze
            
        Returns:
            dict: Analysis results containing:
                - is_appropriate (bool): Whether the image is appropriate
                - quality_score (float): Image quality score (0-1)
                - detected_brands (list): List of detected brands
                - detected_text (list): Any text found in the logo
                - detected_objects (list): Objects detected in the image
        """
        try:
            # Analyze image for inappropriate content
            adult_results = self.client.analyze_image_in_stream(
                image_data,
                visual_features=['Adult']
            )
            
            # Detect brands
            brands = self.client.analyze_image_in_stream(
                image_data,
                features=['Brands']
            )
            
            # Analyze image quality
            quality = self.client.analyze_image_in_stream(
                image_data,
                visual_features=['ImageQuality']
            )
            
            # Detect text
            text = self.client.detect_text_in_stream(image_data)
            
            # Detect objects
            objects = self.client.detect_objects_in_stream(image_data)
            
            return {
                'is_appropriate': not (
                    adult_results.adult.is_adult_content or
                    adult_results.adult.is_racy_content
                ),
                'quality_score': quality.image_quality.quality_score,
                'detected_brands': [
                    {
                        'name': brand.name,
                        'confidence': brand.confidence
                    }
                    for brand in brands.brands
                ],
                'detected_text': [
                    line.text for line in text.regions
                ] if hasattr(text, 'regions') else [],
                'detected_objects': [
                    {
                        'object': obj.object_property,
                        'confidence': obj.confidence
                    }
                    for obj in objects.objects
                ]
            }
            
        except Exception as e:
            logging.error(f"Error analyzing logo with Azure Vision: {str(e)}")
            return None

    def validate_logo(self, image_data, min_quality=0.5):
        """Validate a logo meets quality and appropriateness standards.
        
        This method checks if a logo is appropriate for use and meets
        minimum quality standards.
        
        Args:
            image_data (bytes): Raw image data to validate
            min_quality (float, optional): Minimum quality score (0-1)
                Defaults to 0.5
                
        Returns:
            tuple: (is_valid, reason) where:
                - is_valid (bool): Whether the logo is valid
                - reason (str): Reason for invalidity if not valid
        """
        try:
            results = self.analyze_logo(image_data)
            if not results:
                return False, "Failed to analyze logo"
                
            if not results['is_appropriate']:
                return False, "Logo contains inappropriate content"
                
            if results['quality_score'] < min_quality:
                return False, f"Logo quality score ({results['quality_score']:.2f}) below minimum ({min_quality})"
                
            return True, "Logo is valid"
            
        except Exception as e:
            logging.error(f"Error validating logo: {str(e)}")
            return False, f"Error validating logo: {str(e)}"