"""
video_dwt_controller.py
──────────────────
Video steganography controller using DWT (Discrete Wavelet Transform).
Core logic extracted for API usage.
"""

import os
import sys
import struct
import hashlib
import json
import shutil
import time
from typing import Tuple, List, Dict, Any

import cv2
import numpy as np
import pywt


from storage import OUTPUTS_DIR

#  ENCRYPTION  (AES-256-GCM)


try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False
    print("WARNING: 'cryptography' not installed — using XOR fallback.")
    print("         pip install cryptography\n")

_KEY = hashlib.sha256(b"video-dwt-stego-key-do-not-use-in-prod").digest()


def encrypt_message(plaintext: str) -> bytes:
    data = plaintext.encode("utf-8")
    if HAS_CRYPTO:
        nonce = os.urandom(12)
        ct = AESGCM(_KEY).encrypt(nonce, data, None)
        return nonce + ct
    else:
        ks = (_KEY * ((len(data) // 32) + 1))[:len(data)]
        return bytes(b ^ k for b, k in zip(data, ks))


def decrypt_message(payload: bytes) -> str:
    if HAS_CRYPTO:
        nonce, ct = payload[:12], payload[12:]
        data = AESGCM(_KEY).decrypt(nonce, ct, None)
    else:
        ks = (_KEY * ((len(payload) // 32) + 1))[:len(payload)]
        data = bytes(b ^ k for b, k in zip(payload, ks))
    return data.decode("utf-8")



#  BIT UTILITIES


def _to_bits(data: bytes) -> List[int]:
    return [int(b) for byte in data for b in format(byte, "08b")]


def _bits_to_bytes(bits: List[int]) -> bytes:
    if len(bits) % 8:
        bits = bits + [0] * (8 - len(bits) % 8)
    return bytes(
        int("".join(str(b) for b in bits[i:i+8]), 2)
        for i in range(0, len(bits), 8)
    )



#  DWT EMBED / EXTRACT  (per frame)


WAVELET = "haar"


def _embed_bits_in_frame(frame_bgr: np.ndarray, bits: List[int],
                          bit_offset: int, strength: float) -> Tuple[np.ndarray, int]:
    """
    Embed as many bits as possible into one frame starting at bit_offset.
    Returns (modified_frame, next_bit_offset).
    """
    # Work directly on the Blue channel to avoid OpenCV YCrCb conversion rounding losses
    B = frame_bgr[:, :, 0].astype(np.float64)

    # 1-level DWT
    coeffs = pywt.dwt2(B, WAVELET)
    LL, (LH, HL, HH) = coeffs

    flat = LL.flatten()
    written = 0
    for idx in range(len(flat)):
        if bit_offset + written >= len(bits):
            break
        bit = bits[bit_offset + written]

        val = flat[idx]
        q = round(val / strength)

        # Quantisation-index modulation
        if q % 2 != bit:
            # Shift to the nearest bin that matches our bit
            if val > q * strength:
                q += 1
            else:
                q -= 1

        flat[idx] = q * strength
        written += 1

    LL_mod = flat.reshape(LL.shape)
    B_mod = pywt.idwt2((LL_mod, (LH, HL, HH)), WAVELET)

    # Crop back to original size (idwt2 may add 1 row/col on odd dimensions)
    B_mod = B_mod[:B.shape[0], :B.shape[1]]

    # Safely round and clip before packing back to uint8
    frame_bgr[:, :, 0] = np.clip(np.round(B_mod), 0, 255).astype(np.uint8)

    return frame_bgr, bit_offset + written


def _extract_bits_from_frame(frame_bgr: np.ndarray, count: int,
                               bit_offset: int, strength: float) -> Tuple[List[int], int]:
    """
    Extract `count` bits from one frame.
    Returns (bits_list, next_bit_offset).
    """
    B = frame_bgr[:, :, 0].astype(np.float64)

    coeffs = pywt.dwt2(B, WAVELET)
    LL, _ = coeffs

    flat = LL.flatten()
    bits = []
    for idx in range(len(flat)):
        if len(bits) >= count:
            break

        # Use round() to prevent bit extraction errors
        q = round(flat[idx] / strength)
        bits.append(int(q % 2))

    return bits, bit_offset + len(bits)


def _bits_per_frame(frame_bgr: np.ndarray) -> int:
    """How many bits can one frame hold."""
    h, w = frame_bgr.shape[:2]
    ll_h = (h + 1) // 2
    ll_w = (w + 1) // 2
    return ll_h * ll_w



#  REMUX (copy audio track)


def _remux(video_only: str, audio_source: str, output: str) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        # Copies the video codec directly without altering the pixels
        cmd = (
            f'ffmpeg -y -loglevel error '
            f'-i "{video_only}" '
            f'-i "{audio_source}" '
            f'-c:v copy -c:a copy -map 0:v:0 -map 1:a:0 '
            f'"{output}"'
        )
        ret = os.system(cmd)
        if ret == 0:
            return
    import shutil as _shutil
    _shutil.copy2(video_only, output)



#  PUBLIC API FUNCTIONS


def embed_in_video(
    video_path: str,
    secret: str,
    output_path: str,
    quant_step: int = 32
) -> Dict[str, Any]:
    """
    Embed a secret message into a video using DWT steganography.
    
    Parameters:
    -----------
    video_path : str
        Path to input video file
    secret : str
        Secret message to hide
    output_path : str
        Path where output video will be saved
    quant_step : int
        Quantisation step strength (4-64). Higher = more robust but more visible.
        Default 32.
    
    Returns:
    --------
    dict containing embedding statistics
    """
    start_time = time.time()
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video not found: {video_path}")
    
    strength = float(quant_step)
    
    payload_bytes = encrypt_message(secret)
    payload_len = len(payload_bytes)

    # build bit-stream: [length:4B] [payload] [terminator:4B]
    TERMINATOR = 0xFFFFFFFF
    stream = (
        struct.pack(">I", payload_len) +
        payload_bytes +
        struct.pack(">I", TERMINATOR)
    )
    bits = _to_bits(stream)
    total_bits = len(bits)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ret, test_frame = cap.read()
    if not ret:
        raise ValueError("Cannot read frames from video.")
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    bpf = _bits_per_frame(test_frame)
    max_bits = total_frames * bpf - 64
    if total_bits > max_bits:
        raise ValueError(
            f"Message too long for this video.\n"
            f"  Need : {total_bits} bits\n"
            f"  Have : {max_bits} bits"
        )

    util = round(total_bits / (total_frames * bpf) * 100, 1)

    tmp_path = output_path + ".tmp.avi"

    # Strict Lossless format required for Stego
    out = cv2.VideoWriter(
        tmp_path,
        cv2.VideoWriter_fourcc(*"FFV1"),
        fps,
        (width, height)
    )

    if not out.isOpened():
        out = cv2.VideoWriter(
            tmp_path,
            cv2.VideoWriter_fourcc(*"png "),
            fps,
            (width, height)
        )

    bit_cursor = 0
    frames_used = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if bit_cursor < total_bits:
            frame, bit_cursor = _embed_bits_in_frame(frame, bits, bit_cursor, strength)
            frames_used += 1

        out.write(frame)

    cap.release()
    out.release()

    # Remux using ffmpeg to carry audio over losslessly
    _remux(tmp_path, video_path, output_path)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    # Save tracking parameters
    params_file = output_path.rsplit(".", 1)[0] + "_params.json"
    params = {
        "wavelet": WAVELET,
        "strength": strength,
        "total_bits_embedded": total_bits,
        "payload_len": payload_len,
        "quant_step": quant_step,
    }
    with open(params_file, "w") as f:
        json.dump(params, f, indent=2)

    embedding_time = time.time() - start_time

    return {
        "output_path": output_path,
        "params_file": params_file,
        "resolution": f"{width}x{height}",
        "fps": fps,
        "total_frames": total_frames,
        "frames_used": frames_used,
        "bits_embedded": total_bits,
        "total_bits_capacity": total_frames * bpf,
        "utilization_percent": util,
        "original_chars": len(secret),
        "encrypted_bytes": payload_len,
        "quantisation_step": quant_step,
        "embedding_time": embedding_time
    }


def extract_from_video(
    video_path: str,
    json_path:str,
    quant_step: int = 32
) -> str:
    """
    Extract a secret message from a video using DWT steganography.
    
    Parameters:
    -----------
    video_path : str
        Path to stego video file
    quant_step : int
        Quantisation step used during embedding. Must match!
    
    Returns:
    --------
    str - Extracted secret message
    """
    params_file = json_path
    
    if not os.path.exists(params_file):
        # Try to find params file in same directory with different extension
        base = video_path.rsplit(".", 1)[0]
        # alt_params = base + "_params.json"
        #get alt params from outputs dir
        alt_params = OUTPUTS_DIR / (base.split("/")[-1] + "_params.json")
        if os.path.exists(alt_params):
            params_file = alt_params
        else:
            raise FileNotFoundError(
                f"Params file not found: '{params_file}'\n"
                "Keep the _params.json next to the stego video."
            )
    
    with open(params_file) as f:
        p = json.load(f)
    
    strength = float(quant_step)
    payload_len = p["payload_len"]

    total_bits = (4 + payload_len + 4) * 8

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    all_bits = []
    bits_needed = total_bits

    while len(all_bits) < bits_needed:
        ret, frame = cap.read()
        if not ret:
            break
        bpf = _bits_per_frame(frame)
        want = min(bpf, bits_needed - len(all_bits))
        bits, _ = _extract_bits_from_frame(frame, want, 0, strength)
        all_bits.extend(bits[:want])

    cap.release()

    if len(all_bits) < total_bits:
        raise ValueError(
            f"Not enough frames to extract {total_bits} bits. "
            f"Got {len(all_bits)} bits."
        )

    length_bits = all_bits[:32]
    decoded_len = struct.unpack(">I", _bits_to_bytes(length_bits))[0]

    if decoded_len != payload_len:
        # Try to use payload_len from params instead
        decoded_len = payload_len

    data_bits = all_bits[32: 32 + decoded_len * 8]
    term_bits = all_bits[32 + decoded_len * 8: 32 + decoded_len * 8 + 32]

    terminator = struct.unpack(">I", _bits_to_bytes(term_bits))[0]
    if terminator != 0xFFFFFFFF:
        # Non-critical warning, continue extraction
        pass

    payload_bytes = _bits_to_bytes(data_bits)
    return decrypt_message(payload_bytes)


def get_capacity_info(video_path: str) -> Dict[str, Any]:
    """
    Get capacity information for a video file.
    
    Parameters:
    -----------
    video_path : str
        Path to video file
    
    Returns:
    --------
    dict containing capacity information
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ret, frame = cap.read()
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    if not ret:
        raise ValueError("Could not read video.")
    
    bpf = _bits_per_frame(frame)
    overhead = 64  # length field + terminator, in bits
    max_bits = total_frames * bpf - overhead
    max_bytes = max_bits // 8
    max_chars = max(0, max_bytes - 12 - 16)  # Subtract encryption overhead
    
    return {
        "resolution": f"{width}x{height}",
        "total_frames": total_frames,
        "fps": round(fps, 2),
        "bits_per_frame": bpf,
        "total_bits_capacity": total_frames * bpf,
        "max_payload_bits": max_bits,
        "max_payload_bytes": max_bytes,
        "max_message_chars": max_chars,
        "overhead_bits": overhead
    }