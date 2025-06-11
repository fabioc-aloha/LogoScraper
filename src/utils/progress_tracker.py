import json

class ProgressTracker:
    """Track and persist progress of logo processing operations."""

    def __init__(self, progress_file='progress.json'):
        self.progress_file = progress_file
        self.progress = {'completed': [], 'failed': []}
        self.load_progress()

    def load_progress(self):
        """Load progress from the progress file."""
        try:
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.progress = {'completed': [], 'failed': []}

    def save_progress(self):
        """Save progress to the progress file."""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f)

    def mark_completed(self, id):
        """Mark an ID as successfully processed."""
        if id not in self.progress['completed']:
            self.progress['completed'].append(id)
            self.save_progress()

    def mark_failed(self, id):
        """Mark an ID as failed."""
        if id not in self.progress['failed']:
            self.progress['failed'].append(id)
            self.save_progress()

    def is_processed(self, id):
        """Check if an ID has already been processed."""
        return id in self.progress['completed'] or id in self.progress['failed']