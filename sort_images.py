import os
import shutil
import sys

def sort_drone_images(folder_path):
    """
    Sorts drone images into Thermal, Visual, and Wide folders.
    Files that don't match any category go to Other folder.
    """
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' does not exist!")
        return False
    
    # Create folders if they don't exist
    thermal_dir = os.path.join(folder_path, "Thermal")
    visual_dir = os.path.join(folder_path, "Visual")
    wide_dir = os.path.join(folder_path, "Wide")
    other_dir = os.path.join(folder_path, "Other")
    
    os.makedirs(thermal_dir, exist_ok=True)
    os.makedirs(visual_dir, exist_ok=True)
    os.makedirs(wide_dir, exist_ok=True)
    
    # Process all files in the folder
    moved_count = 0
    skipped_count = 0
    other_count = 0
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if it's a file (not a folder)
        if os.path.isfile(file_path):
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
            
            # Check if destination file already exists
            if os.path.exists(destination):
                print(f"Skipped (already exists): {filename}")
                skipped_count += 1
            else:
                try:
                    shutil.move(file_path, destination)
                    if category == "Other":
                        print(f"Moved to Other: {filename}")
                        other_count += 1
                    else:
                        print(f"Moved to {category}: {filename}")
                        moved_count += 1
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
                    skipped_count += 1
    
    print(f"\nDone!")
    print(f"Moved to categories: {moved_count} files")
    print(f"Moved to Other: {other_count} files")
    print(f"Skipped: {skipped_count} files")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sort_images.py <folder_path>")
        print("Example: python sort_images.py C:\\Users\\User\\DronePhotos")
    else:
        folder_path = sys.argv[1]
        sort_drone_images(folder_path)