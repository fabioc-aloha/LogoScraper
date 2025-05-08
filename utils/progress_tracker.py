"""Progress Tracking Module

This module provides functionality for tracking and persisting the progress of
logo processing operations. Simplified to focus on core tracking functionality.
"""

import json
import logging
import os
from config import CONFIG

class ProgressTracker:
    """Track and persist progress of logo processing operations."""

    def __init__(self, temp_folder=None, logos_folder=None):
        """Initialize the progress tracker."""
        self.logos_folder = logos_folder 
        self.temp_folder = temp_folder
        self.progress_file = os.path.join(self.temp_folder, CONFIG['PROGRESS_FILE'])
        self.progress = {'completed': [], 'failed': []}
        self.load_progress()
    
    def load_progress(self):
        """Load progress from disk or initialize from existing logos."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    self.progress = json.load(f)
            else:
                # Initialize from existing logos
                if os.path.exists(self.logos_folder):
                    for filename in os.listdir(self.logos_folder):
                        if filename.endswith('.png'):
                            tpid = filename[:-4]  # Remove .png extension
                            if tpid not in self.progress['completed']:
                                self.progress['completed'].append(tpid)
                    if self.progress['completed']:
                        logging.info(f"Initialized progress from {len(self.progress['completed'])} existing logos")
                        self.save_progress()

        except Exception as e:
            logging.error(f"Error loading progress: {str(e)}")
    
    def save_progress(self):
        """Save current progress to disk."""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f)
        except Exception as e:
            logging.error(f"Error saving progress file: {str(e)}")
    
    def mark_completed(self, tpid):
        """Mark a TPID as successfully processed."""
        if tpid not in self.progress['completed']:
            self.progress['completed'].append(tpid)
            self.save_progress()
    
    def mark_failed(self, tpid):
        """Mark a TPID as failed."""
        if tpid not in self.progress['failed']:
            self.progress['failed'].append(tpid)
            self.save_progress()
    
    def is_processed(self, tpid):
        """Check if a TPID has already been processed."""
        return tpid in self.progress['completed'] or tpid in self.progress['failed']