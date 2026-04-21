"""
StegoVault — quality metrics analysis route.

Mounted at /metrics by the app factory.
"""
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from media_metrices import audio_metrics, image_metrics
from metrics import QualityMetrics
from storage import save_upload

router = APIRouter()


@router.post("/analyze")
async def analyze_quality(
    original_file: UploadFile = File(...),
    modified_file: UploadFile = File(...),
):
    """
    Compute quality metrics between an original and stego file.
    Supports both image (PSNR / SSIM / MSE / SNR) and audio (SNR) files.
    """
    orig = save_upload(original_file, "orig")
    modi = save_upload(modified_file, "modi")

    try:
        ext = orig.suffix.lower()

        if ext == ".wav":
            m = audio_metrics(orig, modi)
            if not m:
                return JSONResponse({
                    "success": False,
                    "message": (
                        "Could not compute audio metrics — check that both "
                        "files are valid WAV files with identical dimensions."
                    ),
                })
            return {
                "success"   : True,
                "media_type": "audio",
                "metrics"   : m,
            }

        m = image_metrics(orig, modi)
        if not m:
            return JSONResponse({
                "success": False,
                "message": "Could not load one or both images.",
            })
        return {
            "success"   : True,
            "media_type": "image",
            "metrics"   : m,
            "assessment": QualityMetrics.assess(m["psnr"]),
        }

    finally:
        orig.unlink(missing_ok=True)
        modi.unlink(missing_ok=True)