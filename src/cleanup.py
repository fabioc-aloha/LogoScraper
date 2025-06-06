import os
import shutil
import logging
from src.config import CONFIG

def clean_temp_folder(temp_folder: str) -> None:
    """Remove all files and folders in the temporary directory. Create if missing."""
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder, exist_ok=True)
        logging.info(f"Temporary folder created: {temp_folder}")
        return
    for item in os.listdir(temp_folder):
        path = os.path.join(temp_folder, item)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            logging.error(f"Failed to remove {path}: {e}")
    logging.info("Temporary folder cleared.")
