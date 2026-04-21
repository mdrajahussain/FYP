# """
# StegoVault — steganography embed & extract routes.

# Mounted at /stego by the app factory.
# """
# import time
# from pathlib import Path

# from fastapi import APIRouter, File, Form, UploadFile
# from fastapi.responses import FileResponse, JSONResponse

# from algorithms import (
#     LOSSY_AUDIO_EXTS,
#     LOSSY_IMAGE_EXTS,
#     is_audio_algorithm,
#     normalise_algorithm,
# )
# from ethics import EthicalFilter
# from media_metrices import audio_metrics, image_metrics
# from steganography.system import SteganographySystem
# from storage import OUTPUTS_DIR, normalise_png, save_upload, to_lossless_png
# import json

# router = APIRouter()


# # ── Embed ──────────────────────────────────────────────────────────────────

# @router.post("/embed")
# async def embed(
#     file     : UploadFile = File(...),
#     secret   : str        = Form(...),
#     algorithm: str        = Form("LSB"),
# ):
#     """
#     Embed a secret in an image (LSB / DCT / DWT) or audio (EchoHiding) file.

#     Image rules
#     -----------
#     • JPEG/WebP inputs are auto-converted to PNG before embedding.
#     • Output is always a lossless PNG — do NOT re-save as JPEG/WebP.

#     Audio rules
#     -----------
#     • Input must be a WAV file.
#     • Output is always WAV — do NOT re-encode as MP3/AAC.
#     """
#     raw_src = save_upload(file, "src")
#     src     = None
#     dest    = None

#     try:
#         try:
#             algorithm = normalise_algorithm(algorithm)
#         except ValueError as exc:
#             return JSONResponse({"success": False, "message": str(exc)})

#         safe, reason = EthicalFilter.is_safe(secret)
#         if not safe:
#             return JSONResponse(
#                 {"success": False, "message": f"Content safety: {reason}"}
#             )

#         # ── Audio path (EchoHiding) ──────────────────────────────────────
#         if is_audio_algorithm(algorithm):
#             ext = raw_src.suffix.lower()
#             if ext in LOSSY_AUDIO_EXTS:
#                 return JSONResponse({
#                     "success": False,
#                     "message": (
#                         f"Echo Hiding requires a WAV input file. "
#                         f"'{ext}' is a lossy format that will degrade the echo "
#                         "pattern. Please provide a .wav file."
#                     ),
#                 })
#             if ext != ".wav":
#                 return JSONResponse({
#                     "success": False,
#                     "message": (
#                         f"Echo Hiding only supports WAV input; got '{ext}'."
#                     ),
#                 })

#             src  = raw_src
#             dest = OUTPUTS_DIR / f"embedded_{int(time.time() * 1000)}.wav"

#             t0      = time.perf_counter()
#             details = SteganographySystem.embed(
#                 str(src), secret, str(dest), algorithm
#             )
#             elapsed = time.perf_counter() - t0

#             metrics = audio_metrics(src, dest) if dest.exists() else {}

#             return {
#                 "success"       : True,
#                 "message"       : "Secret embedded successfully.",
#                 "output_file"   : dest.name,
#                 "algorithm"     : algorithm,
#                 "details"       : details,
#                 "metrics"       : metrics,
#                 "embedding_time": elapsed,
#                 "note"          : (
#                     "Keep the output as WAV — re-encoding to MP3/AAC "
#                     "will destroy the hidden data."
#                 ),
#             }

#         # ── Image path (LSB / DCT / DWT) ────────────────────────────────
#         src  = to_lossless_png(raw_src)
#         dest = OUTPUTS_DIR / f"embedded_{int(time.time() * 1000)}.png"

#         t0      = time.perf_counter()
#         details = SteganographySystem.embed(str(src), secret, str(dest), algorithm)
#         elapsed = time.perf_counter() - t0

#         metrics = image_metrics(src, dest) if dest.exists() else {}

#         return {
#             "success"       : True,
#             "message"       : "Secret embedded successfully.",
#             "output_file"   : dest.name,
#             "algorithm"     : algorithm,
#             "details"       : details,
#             "metrics"       : metrics,
#             "embedding_time": elapsed,
#             "note"          : (
#                 "Keep the output as PNG — converting to JPEG/WebP "
#                 "will destroy the hidden data."
#             ),
#         }

#     except Exception as exc:
#         return JSONResponse({"success": False, "message": str(exc)})

#     finally:
#         for p in {raw_src, src} - {None}:
#             if p is not None and p.exists():
#                 p.unlink(missing_ok=True)


# # ── Extract ────────────────────────────────────────────────────────────────

# @router.post("/extract")
# async def extract(
#     file           : UploadFile = File(...),
#     algorithm      : str        = Form("auto"),
#     samples_per_bit: int        = Form(None),
#     #added
#     d0            : int        = Form(None),   # Added: optional d0 parameter
#     d1            : int        = Form(None),   # Added: optional d1 parameter
#     decay         : float      = Form(None),   # Added: optional decay parameter 
# ):
#     """
#     Extract a secret from a stego file produced by /stego/embed.

#     • For image algorithms (LSB / DCT / DWT): upload the PNG output.
#       JPEG/WebP files are rejected — lossy compression destroys hidden bits.

#     • For EchoHiding: upload the WAV output.
#       MP3/AAC files are rejected — lossy encoding destroys the echo pattern.
#     """
#     raw_src = save_upload(file, "ext")
#     norm    = None

#     try:
#         try:
#             algorithm = normalise_algorithm(algorithm)
#         except ValueError as exc:
#             return JSONResponse({"success": False, "message": str(exc)})

#         ext = raw_src.suffix.lower()

#         # ── Audio path ───────────────────────────────────────────────────
#         # if algorithm == "EchoHiding" or ext == ".wav":
#         #     if ext in LOSSY_AUDIO_EXTS:
#         #         return JSONResponse({
#         #             "success": False,
#         #             "message": (
#         #                 "Cannot extract from a lossy audio file — "
#         #                 "MP3/AAC encoding destroys the echo pattern. "
#         #                 "Upload the WAV file produced by the embed step."
#         #             ),
#         #         })
#         #     if ext != ".wav":
#         #         return JSONResponse({
#         #             "success": False,
#         #             "message": (
#         #                 f"Echo Hiding extraction expects a WAV file; got '{ext}'."
#         #             ),
#         #         })

#         #     t0      = time.perf_counter()
#         #     secret  = SteganographySystem.extract(
#         #         str(raw_src), "EchoHiding", samples_per_bit=samples_per_bit
#         #     )
#         #     elapsed = time.perf_counter() - t0

#         #     return {
#         #         "success"        : True,
#         #         "message"        : "Secret extracted successfully.",
#         #         "secret"         : secret,
#         #         "details"        : {"algorithm": "EchoHiding"},
#         #         "extraction_time": elapsed,
#         #     }


#         #updated
#         if algorithm == "EchoHiding" or ext == ".wav":
#             if ext in LOSSY_AUDIO_EXTS:
#                 return JSONResponse({
#                     "success": False,
#                     "message": (
#                         "Cannot extract from a lossy audio file — "
#                         "MP3/AAC encoding destroys the echo pattern. "
#                         "Upload the WAV file produced by the embed step."
#                     ),
#                 })
#             if ext != ".wav":
#                 return JSONResponse({
#                     "success": False,
#                     "message": (
#                         f"Echo Hiding extraction expects a WAV file; got '{ext}'."
#                     ),
#                 })

#             # 🔍 ADD DEBUG CODE HERE - Right after validation, before extraction
#             print("=" * 60)
#             print("🔍 DEBUGGING EXTRACTION")
#             print("=" * 60)
            
#             # Get the original filename from the uploaded file
#             original_filename = file.filename
#             original_stem = original_filename.replace('.wav', '')
            
#             print(f"Original filename: {original_filename}")
#             print(f"Original stem: {original_stem}")
#             print(f"Temp file path: {raw_src}")
            
#             # Look for params file with the ORIGINAL name in outputs directory
#             params_file = Path("outputs") / f"{original_stem}_params.json"
#             print(f"🔍 Looking for params file: {params_file}")
#             print(f"🔍 File exists: {params_file.exists()}")
            
#             params = None
            
#             if params_file.exists():
#                 with open(params_file, 'r') as f:
#                     params = json.load(f)
#                 print(f"✅ Found parameters file: {params_file}")
#                 print(f"Using parameters: spb={params['spb']}, d0={params['d0']}, d1={params['d1']}")
#                 print(f"✅ Loaded params: {params}")
#             else:
#                 print(f"❌ No params file found at: {params_file}")
#                 # Also try without the 'outputs/' prefix as fallback
#                 alt_params_file = Path(f"{original_stem}_params.json")
#                 print(f"🔍 Also checking: {alt_params_file}")
#                 if alt_params_file.exists():
#                     params_file = alt_params_file
#                     with open(params_file, 'r') as f:
#                         params = json.load(f)
#                     print(f"✅ Found params file: {params_file}")
            
#             print("=" * 60)
            
#             # Override with explicit parameters if provided
#             if samples_per_bit is not None:
#                 params = params or {}
#                 params['spb'] = samples_per_bit
#             if d0 is not None:
#                 params = params or {}
#                 params['d0'] = d0
#             if d1 is not None:
#                 params = params or {}
#                 params['d1'] = d1
#             if decay is not None:
#                 params = params or {}
#                 params['decay'] = decay
            
#             t0 = time.perf_counter()
            
#             # Extract with proper parameters
#             if params and 'spb' in params and 'd0' in params and 'd1' in params:
#                 print(f"🎯 Extracting with exact parameters: spb={params['spb']}, d0={params['d0']}, d1={params['d1']}")
#                 # Use exact parameters from embedding
#                 secret = SteganographySystem.extract_with_params(
#                     str(raw_src), 
#                     "EchoHiding",
#                     spb=params['spb'],
#                     d0=params['d0'],
#                     d1=params['d1'],
#                     decay=params.get('decay', 0.5)
#                 )
#             else:
#                 print(f"⚠️ No parameters found, falling back to auto-detection")
#                 # Fall back to auto-detection with reasonable defaults
#                 secret = SteganographySystem.extract(
#                     str(raw_src), 
#                     "EchoHiding", 
#                     samples_per_bit=128  # Use 128 as default, not 1024
#                 )
            
#             elapsed = time.perf_counter() - t0

#             return {
#                 "success"        : True,
#                 "message"        : "Secret extracted successfully.",
#                 "secret"         : secret,
#                 "details"        : {
#                     "algorithm": "EchoHiding",
#                     "parameters_used": params if params else "auto-detected"
#                 },
#                 "extraction_time": elapsed,
#             }

#         # ── Image path ───────────────────────────────────────────────────
#         if ext in LOSSY_IMAGE_EXTS:
#             return JSONResponse({
#                 "success": False,
#                 "message": (
#                     "Cannot extract from a JPEG or WebP file — "
#                     "lossy compression destroys the hidden bits. "
#                     "Upload the lossless PNG produced by the embed step."
#                 ),
#             })

#         norm = normalise_png(raw_src)

#         t0      = time.perf_counter()
#         secret  = SteganographySystem.extract(str(norm), algorithm)
#         elapsed = time.perf_counter() - t0

#         return {
#             "success"        : True,
#             "message"        : "Secret extracted successfully.",
#             "secret"         : secret,
#             "details"        : {"algorithm": algorithm},
#             "extraction_time": elapsed,
#         }

#     except Exception as exc:
#         return JSONResponse({"success": False, "message": str(exc)})

#     finally:
#         for p in (raw_src, norm):
#             if p is not None and p.exists():
#                 p.unlink(missing_ok=True)


# # ── Download ───────────────────────────────────────────────────────────────

# @router.get("/download/{filename}")
# async def download(filename: str):
#     from fastapi import HTTPException
#     safe_name = Path(filename).name
#     path      = OUTPUTS_DIR / safe_name
#     if not path.exists():
#         raise HTTPException(status_code=404, detail="File not found.")
#     media_type = (
#         "audio/wav"
#         if safe_name.lower().endswith(".wav")
#         else "application/octet-stream"
#     )
#     return FileResponse(str(path), media_type=media_type, filename=safe_name)




#updated-2
"""
StegoVault — steganography embed & extract routes.
Mounted at /stego by the app factory.
"""

import json
import time
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from algorithms import (
    LOSSY_AUDIO_EXTS,
    LOSSY_IMAGE_EXTS,
    is_audio_algorithm,
    normalise_algorithm,
)
from ethics import EthicalFilter
from media_metrices import audio_metrics, image_metrics
from steganography.echo_hiding import FIXED_D0, FIXED_D1, FIXED_DECAY, FIXED_SPB
from steganography.system import SteganographySystem
from storage import OUTPUTS_DIR, normalise_png, save_upload, to_lossless_png

router = APIRouter()


# ── Embed ──────────────────────────────────────────────────────────────────

@router.post("/embed")
async def embed(
    file     : UploadFile = File(...),
    secret   : str        = Form(...),
    algorithm: str        = Form("LSB"),
):
    """
    Embed a secret in an image (LSB / DCT / DWT) or audio (EchoHiding) file.

    Image rules
    -----------
    • JPEG/WebP inputs are auto-converted to PNG before embedding.
    • Output is always lossless PNG — do NOT re-save as JPEG/WebP.

    Audio rules
    -----------
    • Input must be a WAV file.
    • Output is always WAV — do NOT re-encode as MP3/AAC.
    """
    raw_src = save_upload(file, "src")
    src     = None
    dest    = None

    try:
        try:
            algorithm = normalise_algorithm(algorithm)
        except ValueError as exc:
            return JSONResponse({"success": False, "message": str(exc)})

        safe, reason = EthicalFilter.is_safe(secret)
        if not safe:
            return JSONResponse(
                {"success": False, "message": f"Content safety: {reason}"}
            )

        # ── Audio path ───────────────────────────────────────────────────
        if is_audio_algorithm(algorithm):
            ext = raw_src.suffix.lower()
            if ext in LOSSY_AUDIO_EXTS:
                return JSONResponse({
                    "success": False,
                    "message": (
                        f"Echo Hiding requires a WAV file. '{ext}' is lossy "
                        "and will degrade the echo pattern."
                    ),
                })
            if ext != ".wav":
                return JSONResponse({
                    "success": False,
                    "message": f"Echo Hiding only supports WAV input; got '{ext}'.",
                })

            src  = raw_src
            dest = OUTPUTS_DIR / f"embedded_{int(time.time() * 1000)}.wav"

            t0      = time.perf_counter()
            details = SteganographySystem.embed(str(src), secret, str(dest), algorithm)
            elapsed = time.perf_counter() - t0

            metrics = audio_metrics(src, dest) if dest.exists() else {}

            return {
                "success"       : True,
                "message"       : "Secret embedded successfully.",
                "output_file"   : dest.name,
                "algorithm"     : algorithm,
                "details"       : details,
                "metrics"       : metrics,
                "embedding_time": elapsed,
                "note"          : (
                    "Keep the output as WAV — re-encoding to MP3/AAC "
                    "will destroy the hidden data."
                ),
            }

        # ── Image path ───────────────────────────────────────────────────
        src  = to_lossless_png(raw_src)
        dest = OUTPUTS_DIR / f"embedded_{int(time.time() * 1000)}.png"

        t0      = time.perf_counter()
        details = SteganographySystem.embed(str(src), secret, str(dest), algorithm)
        elapsed = time.perf_counter() - t0

        metrics = image_metrics(src, dest) if dest.exists() else {}

        return {
            "success"       : True,
            "message"       : "Secret embedded successfully.",
            "output_file"   : dest.name,
            "algorithm"     : algorithm,
            "details"       : details,
            "metrics"       : metrics,
            "embedding_time": elapsed,
            "note"          : (
                "Keep the output as PNG — converting to JPEG/WebP "
                "will destroy the hidden data."
            ),
        }

    except Exception as exc:
        return JSONResponse({"success": False, "message": str(exc)})

    finally:
        for p in {raw_src, src} - {None}:
            if p is not None and p.exists():
                p.unlink(missing_ok=True)


# ── Extract ────────────────────────────────────────────────────────────────

@router.post("/extract")
async def extract(
    file           : UploadFile = File(...),
    algorithm      : str        = Form("auto"),
    samples_per_bit: int        = Form(None),
    d0             : int        = Form(None),
    d1             : int        = Form(None),
    decay          : float      = Form(None),
):
    """
    Extract a secret from a stego file produced by /stego/embed.

    • Image (LSB / DCT / DWT): upload the PNG output.
    • EchoHiding: upload the WAV output.
    """
    raw_src = save_upload(file, "ext")
    norm    = None

    try:
        try:
            algorithm = normalise_algorithm(algorithm)
        except ValueError as exc:
            return JSONResponse({"success": False, "message": str(exc)})

        ext = raw_src.suffix.lower()

        # ── Audio path ───────────────────────────────────────────────────
        if algorithm == "EchoHiding" or ext == ".wav":
            if ext in LOSSY_AUDIO_EXTS:
                return JSONResponse({
                    "success": False,
                    "message": (
                        "Cannot extract from a lossy audio file — "
                        "MP3/AAC destroys the echo pattern. "
                        "Upload the WAV produced by the embed step."
                    ),
                })
            if ext != ".wav":
                return JSONResponse({
                    "success": False,
                    "message": f"Echo Hiding expects a WAV file; got '{ext}'.",
                })

            # ── Resolve extraction parameters ────────────────────────────
            # Priority: explicit form fields > params file > FIXED defaults
            params = _load_params_file(file.filename)

            # Form fields override anything from the params file
            if samples_per_bit is not None:
                params["spb"]   = samples_per_bit
            if d0 is not None:
                params["d0"]    = d0
            if d1 is not None:
                params["d1"]    = d1
            if decay is not None:
                params["decay"] = decay

            t0 = time.perf_counter()
            secret = SteganographySystem.extract_with_params(
                str(raw_src),
                "EchoHiding",
                spb=params["spb"],
                d0=params["d0"],
                d1=params["d1"],
                decay=params["decay"],
            )
            elapsed = time.perf_counter() - t0

            return {
                "success"        : True,
                "message"        : "Secret extracted successfully.",
                "secret"         : secret,
                "details"        : {
                    "algorithm"       : "EchoHiding",
                    "parameters_used" : params,
                },
                "extraction_time": elapsed,
            }

        # ── Image path ───────────────────────────────────────────────────
        if ext in LOSSY_IMAGE_EXTS:
            return JSONResponse({
                "success": False,
                "message": (
                    "Cannot extract from a JPEG or WebP file — "
                    "lossy compression destroys the hidden bits. "
                    "Upload the PNG produced by the embed step."
                ),
            })

        norm = normalise_png(raw_src)

        t0      = time.perf_counter()
        secret  = SteganographySystem.extract(str(norm), algorithm)
        elapsed = time.perf_counter() - t0

        return {
            "success"        : True,
            "message"        : "Secret extracted successfully.",
            "secret"         : secret,
            "details"        : {"algorithm": algorithm},
            "extraction_time": elapsed,
        }

    except Exception as exc:
        return JSONResponse({"success": False, "message": str(exc)})

    finally:
        for p in (raw_src, norm):
            if p is not None and p.exists():
                p.unlink(missing_ok=True)


# ── Download ───────────────────────────────────────────────────────────────

@router.get("/download/{filename}")
async def download(filename: str):
    from fastapi import HTTPException
    safe_name = Path(filename).name
    path      = OUTPUTS_DIR / safe_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    media_type = (
        "audio/wav"
        if safe_name.lower().endswith(".wav")
        else "application/octet-stream"
    )
    return FileResponse(str(path), media_type=media_type, filename=safe_name)


# ── Helpers ────────────────────────────────────────────────────────────────

def _load_params_file(uploaded_filename: str) -> dict:
    """
    Try to load the _params.json sidecar saved alongside the embedded WAV.
    Falls back to FIXED defaults if the file cannot be found.

    The embed step saves  outputs/<stem>_params.json  next to the WAV.
    When the user re-uploads that WAV for extraction, the original filename
    is used to locate the matching params file.
    """
    stem        = Path(uploaded_filename).stem          # e.g. "embedded_1775325731712"
    params_path = OUTPUTS_DIR / f"{stem}_params.json"

    if params_path.exists():
        try:
            with open(params_path) as fh:
                data = json.load(fh)
            # Normalise key name (params file uses "spb")
            return {
                "spb"  : int(data["spb"]),
                "d0"   : int(data["d0"]),
                "d1"   : int(data["d1"]),
                "decay": float(data.get("decay", FIXED_DECAY)),
            }
        except Exception:
            pass  # Fall through to defaults

    # No params file — use the FIXED defaults baked into echo_hiding.py
    return {
        "spb"  : FIXED_SPB,
        "d0"   : FIXED_D0,
        "d1"   : FIXED_D1,
        "decay": FIXED_DECAY,
    }