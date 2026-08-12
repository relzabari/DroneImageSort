# DroneImageSort

A Python utility to automatically sort drone images into categories based on their file naming convention.

## Features

- **Command-line interface** - Quick sorting from terminal
- **Graphical User Interface (GUI)** - Easy-to-use visual interface with colorful design
- Automatically sorts images into **Thermal**, **Visual**, and **Wide** folders
- Moves unrecognized images to an **Other** folder
- Skips files that already exist in the destination folder
- Comprehensive error handling and logging
- Optional destination folder selection
- Real-time log display in GUI

## Image Categories

- **Thermal**: Images ending with `_t.jpg` (thermal camera)
- **Visual**: Images ending with `_v.jpg` or `_z.jpg` (visual/zoom camera)
- **Wide**: Images ending with `_w.jpg` (wide camera)
- **Other**: Any other files that don't match the above patterns

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DroneImageSort.git
cd DroneImageSort
```

2. No external dependencies required! The project uses only Python standard library.

## Usage

### GUI Mode (Recommended for most users)

```bash
python gui.py
```

The GUI provides a user-friendly interface to:
1. Select source folder containing drone images
2. Optionally select destination folder (defaults to source folder)
3. View real-time sorting progress and logs
4. View complete log file after sorting

### Command-Line Mode

```bash
python sort_images.py <source_folder> [destination_folder]
```

#### Examples

Sort images in place:
```bash
python sort_images.py C:\Users\User\DronePhotos
```

Sort images to a different destination:
```bash
python sort_images.py C:\Users\User\DronePhotos C:\Users\User\SortedPhotos
```

## Output

The script provides a summary of the sorting operation:
- Number of files moved to each category
- Number of files moved to Other folder
- Number of skipped files (already existing or errors)

## Logging

The script includes comprehensive logging functionality:
- **Console Output**: Real-time updates of important operations (INFO level)
- **Log Files**: Detailed logs are saved to `logs/` directory with timestamp
  - Format: `drone_sort_YYYYMMDD_HHMMSS.log`
  - Includes DEBUG, INFO, WARNING, and ERROR level messages
  
Log levels:
- **DEBUG**: Detailed information about file processing
- **INFO**: General operational information (file movements, statistics)
- **WARNING**: Skipped files (already exist)
- **ERROR**: Errors encountered during execution

## GUI Features

- **Welcome Screen**: Colorful welcome interface with title and instructions
- **Source Selection**: Browse and select source folder containing images
- **Destination Selection**: Optional destination folder selection
- **Progress Display**: Real-time output log showing sorting progress
- **Completion Options**: View full log file or sort another folder

## Requirements

- Python 3.9+
- No external dependencies (uses only standard library: `tkinter`, `logging`, `shutil`, `os`, `sys`)

## Project Structure

- `sorting_engine.py` - UI-independent classification and file-moving logic
- `app_logging.py` - Shared logging setup and result summaries
- `sort_images.py` - Command-line interface
- `gui.py` - Tkinter graphical interface and custom folder picker
- `tests/` - Automated unit tests for classification, conflicts, errors, and destinations

## Tests

Run the automated test suite from the project directory:

```bash
python -m unittest discover -v
```

## License

MIT License

