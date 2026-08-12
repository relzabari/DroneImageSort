import filecmp
import os
import shutil
from dataclasses import dataclass, field
from typing import Callable, Optional


ProgressCallback = Callable[[str, str], None]


@dataclass
class SortResult:
    source_folder: str
    destination_folder: str
    total_files: int = 0
    moved_to_categories: int = 0
    moved_to_other: int = 0
    identical_skipped: int = 0
    renamed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def skipped(self):
        return self.identical_skipped + len(self.errors)

    @property
    def success(self):
        return not self.errors


def classify_filename(filename):
    """Return the destination category for a filename."""
    lower_filename = filename.lower()
    if lower_filename.endswith("_t.jpg"):
        return "Thermal"
    if lower_filename.endswith("_w.jpg"):
        return "Wide"
    if lower_filename.endswith("_v.jpg") or lower_filename.endswith("_z.jpg"):
        return "Visual"
    return "Other"


def resolve_destination(source_path, destination):
    """Return a safe destination and its status: new, identical, or renamed."""
    if not os.path.exists(destination):
        return destination, "new"
    if filecmp.cmp(source_path, destination, shallow=False):
        return destination, "identical"

    directory, filename = os.path.split(destination)
    stem, extension = os.path.splitext(filename)
    suffix = 2
    while True:
        candidate = os.path.join(directory, f"{stem}_{suffix}{extension}")
        if not os.path.exists(candidate):
            return candidate, "renamed"
        if filecmp.cmp(source_path, candidate, shallow=False):
            return candidate, "identical"
        suffix += 1


def sort_drone_images(
    source_folder: str,
    dest_folder: Optional[str] = None,
    progress: Optional[ProgressCallback] = None,
):
    """Sort files and return a detailed result without depending on a UI or logger."""
    destination_folder = dest_folder or source_folder
    result = SortResult(source_folder, destination_folder)

    def report(level, message):
        if progress:
            progress(level, message)

    report("info", "Starting image sorting")
    report("info", f"Source folder: {source_folder}")
    report("info", f"Destination folder: {destination_folder}")

    if not os.path.isdir(source_folder):
        message = f"Source folder '{source_folder}' does not exist or is not a directory."
        result.errors.append(message)
        report("error", message)
        return result

    try:
        os.makedirs(destination_folder, exist_ok=True)
    except OSError as error:
        message = f"Could not create destination folder: {error}"
        result.errors.append(message)
        report("error", message)
        return result

    try:
        filenames = os.listdir(source_folder)
    except OSError as error:
        message = f"Could not read source folder: {error}"
        result.errors.append(message)
        report("error", message)
        return result

    report("info", f"Found {len(filenames)} items in folder")
    for filename in filenames:
        source_path = os.path.join(source_folder, filename)
        if not os.path.isfile(source_path):
            continue

        result.total_files += 1
        category = classify_filename(filename)
        category_dir = os.path.join(destination_folder, category)
        destination = os.path.join(category_dir, filename)

        try:
            os.makedirs(category_dir, exist_ok=True)
            resolved_destination, status = resolve_destination(source_path, destination)
            if status == "identical":
                result.identical_skipped += 1
                report("info", f"Skipped (identical file already exists): {filename}")
                continue

            if status == "renamed":
                report(
                    "info",
                    f"Name conflict: {filename} will be saved as "
                    f"{os.path.basename(resolved_destination)}",
                )

            shutil.move(source_path, resolved_destination)
            if status == "renamed":
                result.renamed += 1
            if category == "Other":
                result.moved_to_other += 1
            else:
                result.moved_to_categories += 1
            report("info", f"Moved to {category}: {os.path.basename(resolved_destination)}")
        except OSError as error:
            message = f"Error moving {filename}: {error}"
            result.errors.append(message)
            report("error", message)

    return result
