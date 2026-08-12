import os
import shutil
import sys
import logging
from datetime import datetime

def setup_logging(log_dir=None):
    """
    Setup logging configuration with both file and console handlers
    """
    if log_dir is None:
        log_dir = os.getcwd()
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("DroneImageSort")
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create file handler
    log_file = os.path.join(log_dir, "logs", f"drone_sort_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Create console handler (only for CLI usage)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger, log_file

def sort_drone_images(source_folder, logger=None, dest_folder=None):
    """
    Sorts drone images from source folder into Thermal, Visual, and Wide folders.
    Files that don't match any category go to Other folder.
    
    Args:
        source_folder: Path to the folder containing source images
        logger: Logger instance (optional)
        dest_folder: Destination folder where sorted folders will be created (optional, defaults to source_folder)
    """
    if logger is None:
        logger = logging.getLogger("DroneImageSort")
    
    # Use destination folder if provided, otherwise use source folder
    if dest_folder is None:
        dest_folder = source_folder
    
    logger.info(f"Starting image sorting")
    logger.info(f"Source folder: {source_folder}")
    logger.info(f"Destination folder: {dest_folder}")
    
    # Check if source folder exists
    if not os.path.exists(source_folder):
        logger.error(f"Source folder '{source_folder}' does not exist!")
        return False
    
    # Check if destination folder exists or create it
    if not os.path.exists(dest_folder):
        try:
            os.makedirs(dest_folder, exist_ok=True)
            logger.info(f"Created destination folder: {dest_folder}")
        except Exception as e:
            logger.error(f"Could not create destination folder: {e}")
            return False
    
    logger.info(f"Processing folder: {source_folder}")
    
    # Create sorted image folders in destination
    thermal_dir = os.path.join(dest_folder, "Thermal")
    visual_dir = os.path.join(dest_folder, "Visual")
    wide_dir = os.path.join(dest_folder, "Wide")
    other_dir = os.path.join(dest_folder, "Other")
    
    os.makedirs(thermal_dir, exist_ok=True)
    os.makedirs(visual_dir, exist_ok=True)
    os.makedirs(wide_dir, exist_ok=True)
    
    logger.debug(f"Created/verified directories: Thermal, Visual, Wide")
    
    # Process all files in the source folder
    moved_count = 0
    skipped_count = 0
    other_count = 0
    total_files = 0
    
    files = os.listdir(source_folder)
    logger.info(f"Found {len(files)} items in folder")
    
    for filename in files:
        file_path = os.path.join(source_folder, filename)
        
        # Check if it's a file (not a folder)
        if os.path.isfile(file_path):
            total_files += 1
            logger.debug(f"Processing file: {filename}")
            
            # Convert to lowercase for case-insensitive comparison
            lower_filename = filename.lower()
            
            destination = None
            category = None
            
            # Check image type and set destination
            if lower_filename.endswith("_t.jpg"):
                destination = os.path.join(thermal_dir, filename)
                category = "Thermal"
                
            elif lower_filename.endswith("_w.jpg"):
                destination = os.path.join(wide_dir, filename)
                category = "Wide"
                
            elif lower_filename.endswith("_v.jpg") or lower_filename.endswith("_z.jpg"):
                destination = os.path.join(visual_dir, filename)
                category = "Visual"
            else:
                # File doesn't match any category
                os.makedirs(other_dir, exist_ok=True)
                destination = os.path.join(other_dir, filename)
                category = "Other"
                logger.debug(f"File '{filename}' does not match standard patterns, moving to Other")
            
            # Check if destination file already exists
            if os.path.exists(destination):
                logger.warning(f"Skipped (already exists): {filename}")
                skipped_count += 1
            else:
                try:
                    shutil.move(file_path, destination)
                    if category == "Other":
                        logger.info(f"Moved to Other: {filename}")
                        other_count += 1
                    else:
                        logger.info(f"Moved to {category}: {filename}")
                        moved_count += 1
                except Exception as e:
                    logger.error(f"Error moving {filename}: {e}")
                    skipped_count += 1
    
    # Summary statistics
    logger.info("=" * 50)
    logger.info("SORTING SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Moved to categories: {moved_count} files")
    logger.info(f"Moved to Other: {other_count} files")
    logger.info(f"Skipped: {skipped_count} files")
    logger.info("=" * 50)
    
    return True

if __name__ == "__main__":
    # Setup logging
    logger, log_file = setup_logging()
    
    logger.info("DroneImageSort started")
    logger.info(f"Log file: {log_file}")
    
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        logger.error("Invalid number of arguments")
        logger.info("Usage: python sort_images.py <source_folder> [destination_folder]")
        logger.info("Example: python sort_images.py C:\\Users\\User\\DronePhotos")
        logger.info("Example: python sort_images.py C:\\Users\\User\\DronePhotos C:\\Users\\User\\SortedPhotos")
        print("Usage: python sort_images.py <source_folder> [destination_folder]")
        print("Example: python sort_images.py C:\\Users\\User\\DronePhotos")
        print("Example: python sort_images.py C:\\Users\\User\\DronePhotos C:\\Users\\User\\SortedPhotos")
    else:
        source_folder = sys.argv[1]
        dest_folder = sys.argv[2] if len(sys.argv) == 3 else None
        
        success = sort_drone_images(source_folder, logger, dest_folder)
        
        if success:
            logger.info("DroneImageSort completed successfully")
        else:
            logger.error("DroneImageSort encountered errors and could not complete")
    
    logger.info("=" * 50)