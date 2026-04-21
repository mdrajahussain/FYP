"""
Video Steganography Routes for embedding and extracting secrets in videos using DWT.
"""

import time
from pathlib import Path
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from steganography.video_dwt import embed_in_video, extract_from_video, get_capacity_info
from storage import OUTPUTS_DIR, save_upload, save_output

router = APIRouter(prefix="/video", tags=["Video Steganography"])


@router.post("/embed")
async def embed_in_video_route(
    file: UploadFile = File(...),
    secret: str = Form(...),
    quant_step: int = Form(32, ge=4, le=64, description="Quantisation step (4-64). Higher = more robust but more visible."),
):
    """
    Embed a secret message into a video file using DWT steganography.
    
    The video is processed frame-by-frame using Discrete Wavelet Transform (DWT)
    on the blue channel. The secret is encrypted with AES-256-GCM before embedding.
    
    Parameters:
    -----------
    file : UploadFile
        Input video file (MP4, AVI, MOV, MKV, WEBM)
    secret : str
        Secret message to hide
    quant_step : int
        Quantisation step (4-64). Default 32.
    """
    raw_src = None
    
    try:
        # Save uploaded file
        raw_src = save_upload(file, "vid_src")
        
        # Validate file extension
        ext = raw_src.suffix.lower()
        if ext not in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return JSONResponse({
                "success": False,
                "message": f"Unsupported video format: {ext}. Use MP4, AVI, MOV, MKV, or WEBM."
            })
        
        # Check capacity before embedding
        try:
            capacity = get_capacity_info(str(raw_src))
            # Rough estimate: each character ~1 byte after encryption
            if len(secret) > capacity["max_message_chars"]:
                return JSONResponse({
                    "success": False,
                    "message": f"Secret too long. Max {capacity['max_message_chars']} characters for this video.",
                    "capacity": capacity
                })
        except Exception as cap_err:
            # Continue anyway, the embed function will validate properly
            pass
        
        # Generate output filename
        output_filename = f"embedded_{int(time.time() * 1000)}.avi"
        output_path = OUTPUTS_DIR / output_filename
        
        # Embed secret
        result = embed_in_video(
            video_path=str(raw_src),
            secret=secret,
            output_path=str(output_path),
            quant_step=quant_step
        )
        
        return {
            "success": True,
            "message": "Secret embedded successfully.",
            "output_file": output_filename,
            "algorithm": "DWT-Video",
            "details": {
                "quantisation_step": result["quantisation_step"],
                "bits_embedded": result["bits_embedded"],
                "total_bits_capacity": result["total_bits_capacity"],
                "utilization_percent": result["utilization_percent"],
                "frames_used": result["frames_used"],
                "total_frames": result["total_frames"],
                "resolution": result["resolution"],
                "fps": result["fps"],
                "original_chars": result["original_chars"],
                "encrypted_bytes": result["encrypted_bytes"],
                "embedding_time_ms": round(result["embedding_time"] * 1000, 2)
            },
            "note": "The output is saved as AVI with lossless codec. Re-encoding will destroy the hidden data."
        }
        
    except ValueError as e:
        return JSONResponse({"success": False, "message": str(e)})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Embedding failed: {str(e)}"})
    finally:
        if raw_src and raw_src.exists():
            raw_src.unlink()


@router.post("/extract")
async def extract_from_video_route(
    file: UploadFile = File(...),
    quant_step: int = Form(32, ge=4, le=64, description="Quantisation step used during embedding. Must match!"),
):
    """
    Extract a secret message from a video file.
    
    The video must be the exact output from the embed endpoint (same quant_step).
    The parameters file (_params.json) must be present alongside the video.
    
    Parameters:
    -----------
    file : UploadFile
        Stego video file (must be the exact output from embed endpoint)
    quant_step : int
        Quantisation step used during embedding. Must match!
    """
    raw_src = None
    
    try:
        # Save uploaded file
        # raw_src = save_upload(file, "vid_ext")
        raw_src = save_output(file, "vid_ext")
        json_path = raw_src.with_name(f"{raw_src.stem}_params.json")
        # Split the stem (vid_ext_1775494991907_embedded_1775494823327)
        parts = raw_src.stem.split("_")

        # Grab only the last two parts: ['embedded', '1775494823327']
        # Then join them and add the suffix
        clean_name = f"{parts[-2]}_{parts[-1]}_params.json"

        # Join it back to the same directory
        json_path = raw_src.parent / clean_name

        print(f"Extracting from video: {raw_src}, using params: {json_path} with quant_step={quant_step}")
        
        # Validate file extension
        ext = raw_src.suffix.lower()
        if ext not in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return JSONResponse({
                "success": False,
                "message": f"Unsupported video format: {ext}. Use MP4, AVI, MOV, MKV, or WEBM."
            })
        
        # Extract secret
        secret = extract_from_video(
            video_path=str(raw_src),
            json_path=json_path,
            quant_step=quant_step,

        )
        
        return {
            "success": True,
            "message": "Secret extracted successfully.",
            "secret": secret,
            "algorithm": "DWT-Video",
            "details": {
                "quantisation_step": quant_step
            }
        }
        
    except FileNotFoundError as e:
        return JSONResponse({
            "success": False, 
            "message": str(e),
            "note": "The parameters file (_params.json) must be uploaded alongside the video."
        })
    except ValueError as e:
        return JSONResponse({"success": False, "message": str(e)})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Extraction failed: {str(e)}"})
    finally:
        if raw_src and raw_src.exists():
            raw_src.unlink()


@router.post("/capacity")
async def get_video_capacity(
    file: UploadFile = File(...),
):
    """
    Get the maximum message capacity for a video file.
    
    Returns information about how many characters can be hidden in the video.
    """
    raw_src = None
    
    try:
        # Save uploaded file
        raw_src = save_upload(file, "vid_cap")
        
        # Validate file extension
        ext = raw_src.suffix.lower()
        if ext not in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return JSONResponse({
                "success": False,
                "message": f"Unsupported video format: {ext}. Use MP4, AVI, MOV, MKV, or WEBM."
            })
        
        # Get capacity info
        capacity = get_capacity_info(str(raw_src))
        
        return {
            "success": True,
            "capacity": capacity,
            "note": "Actual capacity may vary slightly due to encryption overhead."
        }
        
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Failed to analyze video: {str(e)}"})
    finally:
        if raw_src and raw_src.exists():
            raw_src.unlink()


@router.get("/download/{filename}")
async def download_stego_video(filename: str):
    """
    Download an embedded video file.
    
    Parameters:
    -----------
    filename : str
        Filename of the embedded video (from embed response)
    """
    file_path = OUTPUTS_DIR / filename
    
    if not file_path.exists():
        return JSONResponse({"success": False, "message": "File not found."})
    
    return FileResponse(
        path=str(file_path),
        media_type="video/x-msvideo",
        filename=filename
    )