"""Unit tests for the core image-processing logic of icon_converter."""

import io
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from icon_converter import (
    build_output_path,
    process_array,
    process_pil_image,
    save_processed,
)


def make_rgba(size=(4, 4), color=(30, 30, 30, 255)):
    """Create a solid RGBA image."""
    return Image.new("RGBA", size, color)


class ProcessArrayTest(unittest.TestCase):
    def test_dark_gray_pixel_is_lightened(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (30, 30, 30, 255)  # dark gray, opaque
        out = process_array(arr, direction="dark_to_light")
        r, g, b, a = out[0, 0]
        self.assertGreater(r, 30)
        self.assertGreater(g, 30)
        self.assertGreater(b, 30)
        self.assertEqual(a, 255)

    def test_light_gray_pixel_is_darkened(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (200, 200, 200, 255)  # light gray, opaque
        out = process_array(arr, direction="light_to_dark")
        r, g, b, a = out[0, 0]
        self.assertLess(r, 200)
        self.assertLess(g, 200)
        self.assertLess(b, 200)
        self.assertEqual(a, 255)

    def test_transparent_pixel_is_untouched(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (30, 30, 30, 0)  # transparent
        out = process_array(arr)
        self.assertEqual(tuple(out[0, 0]), (30, 30, 30, 0))

    def test_colorful_pixel_is_untouched(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (200, 20, 20, 255)  # saturated red, high variance
        out = process_array(arr)
        self.assertEqual(tuple(out[0, 0]), (200, 20, 20, 255))

    def test_light_pixel_is_untouched_in_dark_to_light(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (200, 200, 200, 255)  # light gray, above avg threshold
        out = process_array(arr, direction="dark_to_light")
        self.assertEqual(tuple(out[0, 0]), (200, 200, 200, 255))

    def test_dark_pixel_is_untouched_in_light_to_dark(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (30, 30, 30, 255)  # dark gray, below avg threshold
        out = process_array(arr, direction="light_to_dark")
        self.assertEqual(tuple(out[0, 0]), (30, 30, 30, 255))

    def test_thresholds_are_respected(self):
        arr = np.zeros((1, 1, 4), dtype=np.uint8)
        arr[0, 0] = (100, 100, 100, 255)
        # With a very low avg threshold, this pixel should NOT be converted.
        out = process_array(arr, variance_threshold=30, avg_threshold=50,
                            direction="dark_to_light")
        self.assertEqual(tuple(out[0, 0]), (100, 100, 100, 255))


class ProcessPilImageTest(unittest.TestCase):
    def test_returns_rgba(self):
        img = make_rgba()
        out = process_pil_image(img)
        self.assertEqual(out.mode, "RGBA")
        self.assertEqual(out.size, img.size)

    def test_converts_rgb_input(self):
        img = Image.new("RGB", (4, 4), (30, 30, 30))
        out = process_pil_image(img)
        self.assertEqual(out.mode, "RGBA")


class SaveProcessedTest(unittest.TestCase):
    def test_png_roundtrip(self, tmp_path=None):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "icon.png"
            make_rgba().save(src)
            dst = Path(d) / "icon_dark.png"
            save_processed(src, dst, output_format="PNG", direction="light_to_dark")
            self.assertTrue(dst.exists())
            with Image.open(dst) as img:
                self.assertEqual(img.mode, "RGBA")

    def test_jpg_flattens_alpha(self):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "icon.png"
            make_rgba().save(src)
            dst = Path(d) / "icon_dark.jpg"
            save_processed(src, dst, output_format="JPG", direction="light_to_dark")
            self.assertTrue(dst.exists())
            with Image.open(dst) as img:
                self.assertEqual(img.mode, "RGB")

    def test_animated_gif_preserves_frames(self):
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "anim.gif"
            frames = [make_rgba((4, 4), (30, 30, 30, 255)),
                      make_rgba((4, 4), (60, 60, 60, 255))]
            frames[0].save(src, save_all=True, append_images=frames[1:],
                           duration=100, loop=0)
            dst = Path(d) / "anim_dark.gif"
            save_processed(src, dst, output_format="GIF", direction="light_to_dark")
            self.assertTrue(dst.exists())
            with Image.open(dst) as img:
                self.assertEqual(img.n_frames, 2)


class BuildOutputPathTest(unittest.TestCase):
    def test_default_dir_is_source(self):
        src = Path("/tmp/icon.png")
        out = build_output_path(src, None, "PNG", direction="light_to_dark")
        self.assertEqual(out, Path("/tmp/icon_dark.png"))

    def test_custom_dir(self):
        src = Path("/tmp/icon.png")
        out = build_output_path(src, Path("/out"), "PNG", direction="light_to_dark")
        self.assertEqual(out, Path("/out/icon_dark.png"))

    def test_jpg_suffix(self):
        src = Path("/tmp/icon.png")
        out = build_output_path(src, None, "JPG", direction="light_to_dark")
        self.assertEqual(out, Path("/tmp/icon_dark.jpg"))

    def test_dark_to_light_suffix(self):
        src = Path("/tmp/icon.png")
        out = build_output_path(src, None, "PNG", direction="dark_to_light")
        self.assertEqual(out, Path("/tmp/icon_light.png"))


if __name__ == "__main__":
    unittest.main()
