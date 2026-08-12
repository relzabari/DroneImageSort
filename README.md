# DroneImageSort

A Python utility to automatically sort drone images into categories based on their file naming convention.

## Features

- Automatically sorts images into **Thermal**, **Visual**, and **Wide** folders
- Moves unrecognized images to an **Other** folder
- Skips files that already exist in the destination folder
- Comprehensive error handling and logging
- Easy-to-use command-line interface

## Image Categories

- **Thermal**: Images ending with `_t.jpg` (thermal camera)
- **Visual**: Images ending with `_v.jpg` or `_z.jpg` (visual/zoom camera)
- **Wide**: Images ending with `_w.jpg` (wide camera)
- **Other**: Any other files that don't match the above patterns

## Usage

```bash
python sort_images.py <folder_path>
```

### Example

```bash
python sort_images.py C:\Users\User\DronePhotos
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DroneImageSort.git
cd DroneImageSort
```

2. Run the script:
```bash
python sort_images.py <your_folder_path>
```

## Output

The script provides a summary of the sorting operation:
- Number of files moved to each category
- Number of files moved to Other folder
- Number of skipped files (already existing or errors)

## Requirements

- Python 3.6+
- No external dependencies

## License

MIT License
