import ctypes
import logging
from pathlib import Path


def install_fonts(font_dir: str) -> None:
    font_dir = Path(font_dir)
    gdi32 = ctypes.WinDLL("gdi32")

    for font_file in font_dir.glob("*.ttf"):
        logging.info(f"Installing font {font_file.as_posix()}")
        gdi32.AddFontResourceW(font_file.as_posix())


def remove_fonts(font_dir: str) -> None:
    font_dir = Path(font_dir)
    gdi32 = ctypes.WinDLL("gdi32")
    for font_file in font_dir.glob("*.ttf"):
        logging.info(f"Removing font {font_file.as_posix()}")
        gdi32.RemoveFontResourceW(font_file.as_posix())
