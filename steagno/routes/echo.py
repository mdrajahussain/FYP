"""
route.py
────────
FastAPI router for Echo Hiding steganography.

Mount in main.py:
    from route import router as echo_router
    app.include_router(echo_router)
"""

import json
import time
from pathlib import Path
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

from steganography.echo import embed, extract

router = APIRouter(prefix="/echo", tags=["Echo Hiding"])

# Output directory
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)


#  SCHEMAS


class EmbedResponse(BaseModel):
    success: bool
    message: str
    output_file: str
    algorithm: str
    details: dict
    metrics: dict
    embedding_time: float
    note: str


class ExtractResponse(BaseModel):
    success: bool
    message: str
    secret: str
    details: dict
    extraction_time: float


#  EMBED
#  POST /echo/embed
#  Form fields:  secret (str)
#  File field:   audio  (WAV)
#  Returns:      JSON with file info (similar to image steganography)


@router.post(
    "/embed",
    summary="Embed a secret message into a WAV file",
    response_model=EmbedResponse,
)
async def embed_endpoint(
    audio: UploadFile = File(..., description="Input WAV file (≥30s recommended)"),
    secret: str = Form(..., description="Plaintext message to hide"),
):
    if not audio.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only WAV files are supported.")
    if not secret.strip():
        raise HTTPException(status_code=400, detail="Secret message cannot be empty.")

    audio_bytes = await audio.read()
    start_time = time.perf_counter()

    try:
        stego_bytes, params, stats = embed(audio_bytes, secret)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

    embedding_time = time.perf_counter() - start_time

    # Generate output filename
    timestamp = int(time.time() * 1000)
    output_filename = f"embedded_{timestamp}.wav"
    output_path = OUTPUTS_DIR / output_filename
    
    # Save the stego audio file
    with open(output_path, "wb") as f:
        f.write(stego_bytes)
    
    # Save parameters to JSON file
    params_filename = output_filename.replace(".wav", "_params.json")
    params_path = OUTPUTS_DIR / params_filename
    with open(params_path, "w") as f:
        json.dump(params, f, indent=2)
    
    # Prepare response similar to image steganography
    response = {
        "success": True,
        "message": "Secret embedded successfully.",
        "output_file": output_filename,
        "algorithm": "EchoHiding",
        "details": {
            "algorithm": "EchoHiding",
            "secret_length": len(secret),
            "encrypted_bytes": stats.get("encrypted_bytes", 0),
            "total_bits": stats.get("bits_embedded", 0),
            "bits_used": stats.get("bits_embedded", 0),
            "capacity_used": f"{stats.get('bits_embedded', 0)}/{stats.get('bits_available', 0)} ({stats.get('utilization_pct', 0)}%)",
            "parameters": params,
            "sample_rate": stats.get("sample_rate", 0),
            "duration_s": stats.get("duration_s", 0)
        },
        "metrics": {
            "snr": None,  
            "sample_rate": stats.get("sample_rate", 0)
        },
        "embedding_time": embedding_time,
        "note": "Keep the output as WAV — re-encoding to MP3/AAC will destroy the hidden data."
    }
    
    return JSONResponse(content=response)


#  EXTRACT
#  POST /echo/extract
#  File field:   audio  (stego WAV)
#  Returns:      JSON with extracted secret


@router.post(
    "/extract",
    summary="Extract a hidden message from a stego WAV file",
    response_model=ExtractResponse,
)
async def extract_endpoint(
    audio: UploadFile = File(..., description="Stego WAV file"),
):
    if not audio.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only WAV files are supported.")

    audio_bytes = await audio.read()
    start_time = time.perf_counter()
    
    # Try to find parameters file
    # First, check if the uploaded file is from our system (has _params.json)
    original_filename = audio.filename
    params_filename = original_filename.replace(".wav", "_params.json")
    params_path = OUTPUTS_DIR / params_filename
    
    # If not found, try to find by checking all params files
    if not params_path.exists():
        # Try to find matching params file by looking at the embedded filename pattern
        # This handles cases where the file was downloaded and renamed
        for pf in OUTPUTS_DIR.glob("*_params.json"):
            # Check if there's a matching audio file
            audio_file = pf.parent / pf.name.replace("_params.json", ".wav")
            if audio_file.exists():
                # Use this params file
                params_path = pf
                break
    
    if not params_path.exists():
        raise HTTPException(
            status_code=404, 
            detail="Parameters file not found. Please ensure this file was generated by the /echo/embed endpoint."
        )
    
    # Load parameters
    try:
        with open(params_path, "r") as f:
            params = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load parameters: {e}")
    
    # Extract the secret
    try:
        message = extract(audio_bytes, params)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")
    
    extraction_time = time.perf_counter() - start_time
    
    # Prepare response similar to image steganography
    response = {
        "success": True,
        "message": "Secret extracted successfully.",
        "secret": message,
        "details": {
            "algorithm": "EchoHiding",
            "parameters_used": params
        },
        "extraction_time": extraction_time
    }
    
    return JSONResponse(content=response)


#  DOWNLOAD
#  GET /echo/download/{filename}
#  Returns the stego audio file


@router.get(
    "/download/{filename}",
    summary="Download a stego audio file",
)
async def download_file(filename: str):
    """Download a stego audio file from the outputs directory."""
    safe_name = Path(filename).name
    file_path = OUTPUTS_DIR / safe_name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    
    return Response(
        content=file_path.read_bytes(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
        },
    )