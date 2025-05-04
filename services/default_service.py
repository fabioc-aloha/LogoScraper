import logging
from utils.image_utils import create_default_logo

class DefaultService:
    def __init__(self, target_size):
        self.target_size = target_size  # Keep for consistency with other services

    def get_logo(self, company_name):
        """Create a default logo with company initials"""
        if not company_name:
            return None
        try:
            logo_data = create_default_logo(company_name)
            if logo_data:
                return logo_data
        except Exception as e:
            logging.error(f"Error creating default logo for {company_name}: {str(e)}")
        return None