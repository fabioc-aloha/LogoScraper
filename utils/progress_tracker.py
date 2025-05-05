"""Progress Tracking Module

This module provides functionality for tracking and persisting the progress of
logo processing operations. It maintains a record of completed and failed attempts,
can recover from previous runs, and initializes from existing output files.

The tracker persists state to disk to allow resuming interrupted operations and
provides methods to update and query the processing status of individual items.
"""

import json
import logging
import os


class ProgressTracker:
    """Track and persist progress of logo processing operations.
    
    This class manages the state of logo processing operations, tracking which
    TPIDs have been successfully processed and which have failed. It provides
    persistence through JSON files and can initialize from existing output.
    
    Args:
        progress_file (str): Path to the JSON file for storing progress.
            Defaults to 'download_progress.json'.
        logos_folder (str): Path to the folder containing processed logos.
            Used for initializing state from existing files.
            Defaults to 'logos'.
    
    Attributes:
        progress_file (str): Path to the progress JSON file
        logos_folder (str): Path to the logos output directory
        progress (dict): Dictionary containing lists of completed and failed TPIDs
    """

    def __init__(self, progress_file='download_progress.json', logos_folder='logos'):
        """Initialize the progress tracker with file paths."""
        self.progress_file = progress_file
        self.logos_folder = logos_folder
        self.progress = {'completed': [], 'failed': []}
        self.load_progress()
    
    def load_progress(self):
        """Load progress from disk or initialize from existing logos.
        
        This method attempts to load progress from the JSON file. If the file
        doesn't exist, it will initialize progress by scanning the logos folder
        for existing outputs.
        
        The method handles various edge cases:
        - Missing progress file
        - Corrupt progress file
        - Missing logos folder
        - Existing logos without progress file
        """
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    self.progress = json.load(f)
            else:
                # Initialize from existing logos in folder
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
        """Save current progress to the JSON file.
        
        This method persists the current state to disk, ensuring that progress
        is not lost in case of interruption. Any errors during saving are
        logged but do not interrupt the process.
        """
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f)
        except Exception as e:
            logging.error(f"Error saving progress file: {str(e)}")
    
    def mark_completed(self, tpid):
        """Mark a TPID as successfully processed.
        
        Args:
            tpid (str): The TPID that was successfully processed
        
        This method adds the TPID to the completed list and immediately
        persists the change to disk.
        """
        if tpid not in self.progress['completed']:
            self.progress['completed'].append(tpid)
            self.save_progress()
    
    def mark_failed(self, tpid):
        """Mark a TPID as failed.
        
        Args:
            tpid (str): The TPID that failed processing
        
        This method adds the TPID to the failed list and immediately
        persists the change to disk.
        """
        if tpid not in self.progress['failed']:
            self.progress['failed'].append(tpid)
            self.save_progress()
    
    def is_processed(self, tpid):
        """Check if a TPID has already been processed.
        
        Args:
            tpid (str): The TPID to check
        
        Returns:
            bool: True if the TPID has been either completed or failed,
                False otherwise
        """
        return tpid in self.progress['completed'] or tpid in self.progress['failed']