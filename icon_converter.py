"""Dark Mode Icon Converter.

A desktop application that converts dark/grayish icons into lighter versions so
they remain visible against dark-mode backgrounds.

Features:
    - Batch processing of multiple files at once
    - Drag-and-drop support (when tkinterdnd2 is installed)
    - Configurable conversion thresholds
    - Output directory and format selection
    - Live before/after previews
    - Animated GIF and multi-size ICO support
    - Vectorized (numpy) pixel processing for speed
"""

from __future__ import annotations

import tkinter.filedialog as filedialog
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import customtkinter as ctk
import numpy as np
from PIL import Image, ImageSequence

try:  # Optional drag-and-drop support
    from tkinterdnd2 import DND_FILES, TkinterDnD

    HAS_DND = True
except ImportError:  # pragma: no cover - depends on optional package
    HAS_DND = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PREVIEW_SIZE: Tuple[int, int] = (200, 200)
DEFAULT_VARIANCE_THRESHOLD: int = 30
DEFAULT_AVG_THRESHOLD: int = 160
SUPPORTED_FORMATS: Tuple[str, ...] = ("PNG", "JPG", "ICO", "GIF", "BMP", "WEBP")
IMAGE_FILE_TYPES: Tuple[Tuple[str, str], ...] = (
    ("Image files", "*.png *.jpg *.jpeg *.ico *.gif *.bmp *.webp"),
    ("All files", "*.*"),
)


# ---------------------------------------------------------------------------
# Core image processing (pure functions, unit-testable)
# ---------------------------------------------------------------------------
def process_array(
    rgba: np.ndarray,
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
    avg_threshold: float = DEFAULT_AVG_THRESHOLD,
) -> np.ndarray:
    """Lighten dark/grayish pixels in an RGBA array (H, W, 4) uint8.

    A pixel is converted when it is non-transparent, has low color variance
    (i.e. is grayish) and is darker than ``avg_threshold``. Converted pixels
    are whitened while preserving a slight color tint.
    """
    r = rgba[..., 0].astype(np.float32)
    g = rgba[..., 1].astype(np.float32)
    b = rgba[..., 2].astype(np.float32)
    a = rgba[..., 3]

    avg = (r + g + b) / 3.0
    variance = np.maximum.reduce(
        [np.abs(r - avg), np.abs(g - avg), np.abs(b - avg)]
    )

    mask = (a > 0) & (variance < variance_threshold) & (avg < avg_threshold)

    factor = (255.0 - avg) / 255.0
    new_r = r + (255.0 - r) * factor
    new_g = g + (255.0 - g) * factor
    new_b = b + (255.0 - b) * factor

    out = rgba.copy()
    out[..., 0] = np.where(mask, new_r, r).astype(np.uint8)
    out[..., 1] = np.where(mask, new_g, g).astype(np.uint8)
    out[..., 2] = np.where(mask, new_b, b).astype(np.uint8)
    return out


def process_pil_image(
    img: Image.Image,
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
    avg_threshold: float = DEFAULT_AVG_THRESHOLD,
) -> Image.Image:
    """Process a single PIL image frame, returning a new RGBA image."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    arr = np.array(img)
    processed = process_array(arr, variance_threshold, avg_threshold)
    return Image.fromarray(processed, "RGBA")


def _flatten_alpha(img: Image.Image) -> Image.Image:
    """Composite an RGBA image onto a white background (for JPG output)."""
    background = Image.new("RGB", img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    return background


def save_processed(
    input_path: Path,
    output_path: Path,
    variance_threshold: float = DEFAULT_VARIANCE_THRESHOLD,
    avg_threshold: float = DEFAULT_AVG_THRESHOLD,
    output_format: str = "PNG",
) -> None:
    """Process every frame of ``input_path`` and save to ``output_path``.

    Handles animated GIFs and multi-size ICOs by preserving all frames.
    """
    output_format = output_format.upper()
    if output_format == "JPG":
        output_format = "JPEG"
    with Image.open(input_path) as img:
        frames: List[Image.Image] = [
            process_pil_image(frame, variance_threshold, avg_threshold)
            for frame in ImageSequence.Iterator(img)
        ]

    if output_format == "GIF" and len(frames) > 1:
        frames[0].save(
            output_path,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=img.info.get("duration", 100),
            disposal=2,
        )
    elif output_format == "ICO" and len(frames) > 1:
        frames[0].save(
            output_path, format="ICO", append_images=frames[1:]
        )
    else:
        target = frames[0]
        if output_format in ("JPG", "JPEG"):
            target = _flatten_alpha(target)
        target.save(output_path, format=output_format)


def build_output_path(
    input_path: Path,
    output_dir: Optional[Path],
    output_format: str,
) -> Path:
    """Build the output path with a ``_dark_mode`` suffix and chosen format."""
    output_format = output_format.upper()
    suffix = ".jpg" if output_format in ("JPG", "JPEG") else f".{output_format.lower()}"
    filename = f"{input_path.stem}_dark_mode{suffix}"
    directory = output_dir if output_dir is not None else input_path.parent
    return directory / filename


# ---------------------------------------------------------------------------
# GUI application
# ---------------------------------------------------------------------------
class IconConverter(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Dark Mode Icon Converter")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")

        # State
        self.original_photo = None
        self.converted_photo = None
        self.output_dir: Optional[Path] = None

        self._build_layout()
        self._enable_drag_and_drop()

    # -- UI construction ----------------------------------------------------
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._build_controls()
        self._build_previews()
        self._build_progress()

    def _build_controls(self) -> None:
        controls = ctk.CTkFrame(self.main_frame)
        controls.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        controls.grid_columnconfigure(1, weight=1)

        # File selection
        self.select_button = ctk.CTkButton(
            controls, text="Select Icon(s)", command=self.select_files
        )
        self.select_button.grid(row=0, column=0, padx=10, pady=10)

        self.file_label = ctk.CTkLabel(
            controls, text="No files selected", font=("Arial", 12)
        )
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Output directory
        self.dir_button = ctk.CTkButton(
            controls, text="Output Folder", command=self.select_output_dir
        )
        self.dir_button.grid(row=1, column=0, padx=10, pady=5)

        self.dir_label = ctk.CTkLabel(
            controls, text="Same folder as source", font=("Arial", 12)
        )
        self.dir_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Output format
        self.format_label = ctk.CTkLabel(controls, text="Format:", font=("Arial", 12))
        self.format_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.format_menu = ctk.CTkOptionMenu(
            controls, values=list(SUPPORTED_FORMATS), width=120
        )
        self.format_menu.set("PNG")
        self.format_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Thresholds
        self.variance_label = ctk.CTkLabel(
            controls, text="Gray tolerance:", font=("Arial", 12)
        )
        self.variance_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.variance_slider = ctk.CTkSlider(
            controls, from_=0, to=100, number_of_steps=100
        )
        self.variance_slider.set(DEFAULT_VARIANCE_THRESHOLD)
        self.variance_slider.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.avg_label = ctk.CTkLabel(controls, text="Darkness limit:", font=("Arial", 12))
        self.avg_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        self.avg_slider = ctk.CTkSlider(controls, from_=0, to=255, number_of_steps=255)
        self.avg_slider.set(DEFAULT_AVG_THRESHOLD)
        self.avg_slider.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Process button
        self.process_button = ctk.CTkButton(
            controls, text="Convert", command=self.process_selected, state="disabled"
        )
        self.process_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def _build_previews(self) -> None:
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(1, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        self.original_label = ctk.CTkLabel(
            self.preview_frame, text="Original Icon", font=("Arial", 12)
        )
        self.original_label.grid(row=0, column=0, pady=5)

        self.original_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.original_image_label.grid(row=1, column=0, pady=5)

        self.converted_label = ctk.CTkLabel(
            self.preview_frame, text="Converted Icon", font=("Arial", 12)
        )
        self.converted_label.grid(row=0, column=1, pady=5)

        self.converted_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.converted_image_label.grid(row=1, column=1, pady=5)

    def _build_progress(self) -> None:
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self.main_frame, text="", font=("Arial", 12)
        )
        self.status_label.grid(row=3, column=0, pady=10)

    def _enable_drag_and_drop(self) -> None:
        if not HAS_DND:
            return
        TkinterDnD._require(self)  # enable DnD on the existing Tk root
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_drop)

    # -- Event handlers -----------------------------------------------------
    def _on_drop(self, event) -> None:
        """Handle files dropped onto the window."""
        paths = self.root.tk.splitlist(event.data)
        self._set_files([Path(p) for p in paths])

    def select_files(self) -> None:
        file_paths = filedialog.askopenfilenames(filetypes=IMAGE_FILE_TYPES)
        if file_paths:
            self._set_files([Path(p) for p in file_paths])

    def select_output_dir(self) -> None:
        chosen = filedialog.askdirectory()
        if chosen:
            self.output_dir = Path(chosen)
            self.dir_label.configure(text=str(self.output_dir))

    def _set_files(self, files: Sequence[Path]) -> None:
        self.files = list(files)
        if self.files:
            self.file_label.configure(
                text=f"{len(self.files)} file(s) selected"
            )
            self.process_button.configure(state="normal")
            self._show_preview(self.files[0])
        else:
            self.file_label.configure(text="No files selected")
            self.process_button.configure(state="disabled")

    # -- Preview ------------------------------------------------------------
    def _show_preview(self, file_path: Path) -> None:
        try:
            with Image.open(file_path) as img:
                original = img.convert("RGBA")
                converted = process_pil_image(
                    original,
                    self.variance_slider.get(),
                    self.avg_slider.get(),
                )
            self.original_photo = self._create_preview(
                original, self.original_image_label
            )
            self.converted_photo = self._create_preview(
                converted, self.converted_image_label
            )
        except Exception as exc:  # pragma: no cover - UI error path
            self.status_label.configure(text=f"Preview error: {exc}")

    def _create_preview(self, image: Image.Image, label: ctk.CTkLabel):
        preview = image.copy()
        preview.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
        photo = ctk.CTkImage(
            light_image=preview, dark_image=preview, size=preview.size
        )
        label.configure(image=photo)
        return photo

    # -- Processing ---------------------------------------------------------
    def process_selected(self) -> None:
        if not getattr(self, "files", None):
            return

        variance = self.variance_slider.get()
        avg = self.avg_slider.get()
        output_format = self.format_menu.get()

        total = len(self.files)
        self.progress.set(0)
        self.status_label.configure(text="Processing...")
        self.update_idletasks()

        results: List[str] = []
        errors: List[str] = []

        for index, file_path in enumerate(self.files, start=1):
            try:
                output_path = build_output_path(
                    file_path, self.output_dir, output_format
                )
                save_processed(
                    file_path,
                    output_path,
                    variance_threshold=variance,
                    avg_threshold=avg,
                    output_format=output_format,
                )
                results.append(str(output_path))
            except Exception as exc:
                errors.append(f"{file_path.name}: {exc}")
            self.progress.set(index / total)
            self.update_idletasks()

        self._finish_processing(results, errors)

    def _finish_processing(self, results: List[str], errors: List[str]) -> None:
        if errors:
            self.status_label.configure(
                text=f"Completed with {len(errors)} error(s). "
                f"{len(results)} saved."
            )
        else:
            self.status_label.configure(
                text=f"Success! Saved {len(results)} file(s)."
            )
        self.progress.set(1)


def main() -> None:
    """Launch the application."""
    app = IconConverter()
    app.mainloop()


if __name__ == "__main__":
    main()
