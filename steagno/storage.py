"""
StegoVault — storage paths and upload helpers.
"""
import time
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from algorithms import LOSSY_IMAGE_EXTS

UPLOADS_DIR = Path("uploads")
OUTPUTS_DIR = Path("outputs")

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)


def save_upload(upload: UploadFile, prefix: str) -> Path:
    """Persist an uploaded file to disk and return its path."""
    ts   = int(time.time() * 1000)
    dest = UPLOADS_DIR / f"{prefix}_{ts}_{upload.filename}"
    dest.write_bytes(upload.file.read())
    return dest

def save_output(upload: UploadFile, prefix: str) -> Path:
    """Persist an uploaded file to disk and return its path."""
    ts   = int(time.time() * 1000)
    dest = OUTPUTS_DIR / f"{prefix}_{ts}_{upload.filename}"
    dest.write_bytes(upload.file.read())
    return dest


def to_lossless_png(src: Path) -> Path:
    """Convert a lossy image to PNG in-place. No-op for non-lossy inputs."""
    if src.suffix.lower() not in LOSSY_IMAGE_EXTS:
        return src
    png_path = src.with_suffix(".png")
    Image.open(src).convert("RGB").save(png_path, "PNG")
    src.unlink(missing_ok=True)
    return png_path


def normalise_png(src: Path) -> Path:
    """Re-save as RGB PNG to normalise palette/RGBA modes. Pixel values unchanged."""
    out = src.with_name(src.stem + "_norm.png")
    Image.open(src).convert("RGB").save(out, "PNG")
    return out