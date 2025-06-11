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
                try:
                    os.remove(path)
                except (FileNotFoundError, PermissionError) as e:
                    if isinstance(e, PermissionError):
                        logging.warning(f"Could not remove {path}: file is in use")
                    # Ignore FileNotFoundError - file was already deleted
            elif os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except (FileNotFoundError, PermissionError) as e:
                    if isinstance(e, PermissionError):
                        logging.warning(f"Could not remove directory {path}: one or more files are in use")
                    # Ignore FileNotFoundError - directory was already deleted
        except Exception as e:
            logging.error(f"Failed to remove {path}: {e}")
    logging.info("Temporary folder cleared (some files may have been skipped if in use).")

def cleanup_temp_files(temp_dir):
    """Clean up temporary files created during the scraping process."""
    temp_folder = os.path.join(CONFIG['TEMP_FOLDER'], temp_dir)
    log_file_path = os.path.join(temp_folder, 'logo_scraper.log')
    logging.shutdown()  # Ensure all log handlers are closed before deleting
    try:
        os.remove(log_file_path)
    except FileNotFoundError:
        pass  # Ignore if file does not exist
    except PermissionError:
        print(f"Could not remove {log_file_path}: file is in use")
    except Exception as e:
        print(f"Failed to remove {log_file_path}: {e}")
    clean_temp_folder(temp_folder)
