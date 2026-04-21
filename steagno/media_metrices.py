"""
StegoVault — quality metric helpers for image and audio files.
"""
from pathlib import Path

import cv2
import numpy as np

from metrics import QualityMetrics


def image_metrics(original_path: Path, modified_path: Path) -> dict:
    """Return PSNR, SSIM, MSE, and SNR between two image files."""
    orig = cv2.imread(str(original_path))
    modi = cv2.imread(str(modified_path))
    if orig is None or modi is None:
        return {}

    def to_gray(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

    return {
        "psnr": QualityMetrics.psnr(to_gray(orig), to_gray(modi)),
        "ssim": QualityMetrics.ssim(to_gray(orig), to_gray(modi)),
        "mse" : QualityMetrics.mse(to_gray(orig), to_gray(modi)),
        "snr" : QualityMetrics.snr(to_gray(orig), to_gray(modi)),
    }


def audio_metrics(original_path: Path, modified_path: Path) -> dict:
    """
    Basic SNR metric for audio — sufficient for a quality indicator.
    Returns an empty dict if scipy is unavailable or files cannot be read.
    """
    try:
        from scipy.io import wavfile
        sr1, orig = wavfile.read(str(original_path))
        sr2, modi = wavfile.read(str(modified_path))

        if orig.shape != modi.shape or sr1 != sr2:
            return {}

        orig_f = orig.astype(np.float64)
        modi_f = modi.astype(np.float64)
        noise  = orig_f - modi_f

        signal_power = float(np.mean(orig_f ** 2))
        noise_power  = float(np.mean(noise  ** 2))

        snr = (
            10.0 * np.log10(signal_power / noise_power)
            if noise_power > 0
            else float("inf")
        )
        return {"snr": snr, "sample_rate": sr1}

    except Exception:
        return {}