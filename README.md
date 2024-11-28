# Dark Mode Icon Converter

A simple desktop application that converts dark-colored icons to be more visible in dark mode by making dark and grayish colors lighter.

## Features

- User-friendly GUI interface
- Live preview of both original and converted icons
- Supports various image formats (PNG, JPG, ICO, GIF, BMP)
- Preserves transparency in icons
- Automatically converts dark/gray colors to light colors for better visibility in dark mode

## Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux

## Installation

1. Make sure you have Python installed on your computer. You can download it from [python.org](https://www.python.org/downloads/)

2. Download all these files to a folder:
   - `icon_converter.py`
   - `requirements.txt`

3. Open a terminal/command prompt in that folder and run:
```bash
pip install -r requirements.txt
```

## Usage

1. Open a terminal/command prompt in the folder containing the files and run:
```bash
python icon_converter.py
```

2. Click "Select Icon" to choose your icon file
3. The application will show you a preview of both the original and converted icons
4. The converted icon will be saved in the same folder as the original with '_dark_mode' added to the filename

## How it works

The application analyzes each pixel in your icon:
- Detects dark and grayish colors
- Converts them to lighter shades while preserving slight color variations
- Keeps other colors unchanged
- Maintains transparency

## Troubleshooting

If you get any errors:
1. Make sure Python is installed and added to your system's PATH
2. Try running the pip install command again
3. Make sure you have all the files in the same folder

## Need Help?

If you run into any issues, make sure to:
1. Check if Python is properly installed
2. Verify that all required packages are installed
3. Ensure you're running the command from the correct folder
