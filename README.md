<div align="center">

# 🌙 Dark Mode Icon Converter

**Convert dark/grayish icons into light versions so they stay visible on dark-mode backgrounds.**

A desktop GUI tool built with **CustomTkinter** and **Pillow** that analyzes each pixel, detects dark/gray colors, and lightens them while preserving transparency and color tint.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-4B8BBE?style=for-the-badge&logo=python&logoColor=white)](https://github.com/TomSchimansky/CustomTkinter)
[![Pillow](https://img.shields.io/badge/Pillow-10.0+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python-pillow.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> A small utility for designers and developers who need dark-mode-friendly icon variants.

</div>

---

## 📖 Overview

Dark Mode Icon Converter is a **desktop application** that takes icons with dark or grayish colors and produces lighter versions that remain clearly visible against dark backgrounds. It is ideal for:

- App/website icons that need a dark-mode variant
- Toolbar and menu icons that disappear on dark themes
- Quick batch conversion of icon sets

The tool provides a **live before/after preview**, **batch processing**, **drag-and-drop**, and **configurable thresholds** so you can tune exactly which colors get lightened.

---

## 🎨 Sample Icons

Here are **5 sample icons** generated for this project and converted with the tool. The top row shows the **original dark icons** (nearly invisible on a dark background); the bottom row shows the **converted light versions** produced by the converter.

![Before/After comparison](samples/comparison.png)

| Icon | Original (dark) | Converted (light) |
|---|---|---|
| ⚙️ Gear | `samples/gear.png` | `samples/gear_dark_mode.png` |
| 📁 Folder | `samples/folder.png` | `samples/folder_dark_mode.png` |
| 🏠 Home | `samples/home.png` | `samples/home_dark_mode.png` |
| 👤 User | `samples/user.png` | `samples/user_dark_mode.png` |
| ⭐ Star | `samples/star.png` | `samples/star_dark_mode.png` |

> 💡 **Result:** each dark-gray pixel `(60, 60, 60)` was lightened to `(209, 209, 209)` — a clearly visible light gray — while transparency and shape were fully preserved.

---

## ✨ Features

- User-friendly GUI interface
- Live preview of both original and converted icons
- Batch processing of multiple files at once
- Drag-and-drop file support
- Supports various image formats (PNG, JPG, ICO, GIF, BMP, WEBP)
- Preserves transparency in icons
- Handles animated GIFs and multi-size ICOs
- Configurable conversion thresholds (gray tolerance, darkness limit)
- Choose output folder and output format
- Fast vectorized (numpy) pixel processing

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| GUI | CustomTkinter 5.2+ |
| Imaging | Pillow 10.0+ |
| Pixel processing | NumPy 1.24+ (vectorized) |
| Drag & drop | tkinterdnd2 (optional) |
| Testing | Python `unittest` |

---

## 📁 Repository Structure

```text
dark-mode-icon-enhancer/
├── icon_converter.py          # Main application + core processing logic
├── test_icon_converter.py     # Unit tests for the processing pipeline
├── requirements.txt           # Runtime dependencies
├── pyproject.toml             # Packaging + console entry point
├── samples/                   # Sample icons (original + converted)
│   ├── gear.png / gear_dark_mode.png
│   ├── folder.png / folder_dark_mode.png
│   ├── home.png / home_dark_mode.png
│   ├── user.png / user_dark_mode.png
│   ├── star.png / star_dark_mode.png
│   └── comparison.png         # Before/after grid used in this README
└── README.md                  # This file
```

---

## 🔨 Installation

### Requirements

| Component | Notes |
|---|---|
| Python | 3.8 or higher |
| OS | Windows, macOS, or Linux |

### Install dependencies

```bash
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

---

## 🚀 Usage

### Run the app

```bash
python icon_converter.py
```

### Steps

1. Click **"Select Icon(s)"** to choose your icon files (or drag-and-drop them onto the window)
2. Optionally pick an **output folder** and **output format**
3. Adjust the **conversion thresholds** (gray tolerance, darkness limit) if needed
4. Click **"Convert"**
5. The app shows a preview of both the original and converted icons
6. Converted icons are saved with `_dark_mode` added to the filename

### Programmatic use

The core processing functions can also be used directly:

```python
from pathlib import Path
import icon_converter as ic

ic.save_processed(
    Path("icon.png"),
    Path("icon_dark_mode.png"),
    output_format="PNG",
)
```

---

## ⚙️ How it works

The application analyzes each pixel in your icon:

- Detects **dark and grayish** colors (low RGB variance + low average brightness)
- Converts them to **lighter shades** while preserving slight color variations
- Keeps other colors unchanged
- Maintains transparency

The pixel loop is **vectorized with NumPy** for speed, and multi-frame images (animated GIFs, multi-size ICOs) are processed frame-by-frame.

---

## 🧪 Running tests

```bash
python -m unittest test_icon_converter
```

The suite covers pixel conversion logic, transparency handling, format round-trips, animated GIF preservation, and output-path building.

---

## ⚠️ Troubleshooting

If you get any errors:

1. Make sure Python is installed and added to your system's PATH
2. Try running the `pip install` command again
3. Make sure you have all the files in the same folder
4. For drag-and-drop support, ensure `tkinterdnd2` is installed

---

## 📄 License

MIT

---

<div align="center">
  Made with ❤️ for dark-mode-friendly icons
</div>
