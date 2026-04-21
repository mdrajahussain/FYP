"""
echo_hiding

Work for audio in .wav format with more then 30s length

Core Echo Hiding steganography logic.
"""

import os
import struct
import hashlib
import base64
import json
from typing import Tuple

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

# ══════════════════════════════════════════════════════════════════════════════
#  ENCRYPTION  (AES-256-GCM with XOR fallback)
# ══════════════════════════════════════════════════════════════════════════════

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

_KEY = hashlib.sha256(b"echo-stego-key-do-not-use-in-prod").digest()


def encrypt_message(plaintext: str) -> str:
    data = plaintext.encode("utf-8")
    if HAS_CRYPTO:
        nonce   = os.urandom(12)
        ct      = AESGCM(_KEY).encrypt(nonce, data, None)
        payload = nonce + ct
    else:
        ks      = (_KEY * ((len(data) // 32) + 1))[:len(data)]
        payload = bytes(b ^ k for b, k in zip(data, ks))
    return base64.b64encode(payload).decode("ascii")


def decrypt_message(encoded: str) -> str:
    payload = base64.b64decode(encoded.encode("ascii"))
    if HAS_CRYPTO:
        nonce, ct = payload[:12], payload[12:]
        data      = AESGCM(_KEY).decrypt(nonce, ct, None)
    else:
        ks   = (_KEY * ((len(payload) // 32) + 1))[:len(payload)]
        data = bytes(b ^ k for b, k in zip(payload, ks))
    return data.decode("utf-8")


def _encrypted_byte_size(plaintext: str) -> int:
    raw = len(plaintext.encode("utf-8"))
    return int((12 + raw + 16) * 4 / 3) + 4


# ══════════════════════════════════════════════════════════════════════════════
#  PARAMETER SELECTION  (SR-aware)
# ══════════════════════════════════════════════════════════════════════════════

_LADDER_44K = [
    ( 512,  40, 101),
    ( 768,  55, 138),
    (1024,  60, 153),
    (1536,  80, 203),
    (2048, 100, 251),
]

_LADDER_48K = [
    ( 768,  44, 110),
    (1024,  60, 150),
    (1536,  82, 210),
    (2048, 108, 272),
    (3072, 136, 340),
]

_MAX_UTIL   = 0.50
_MIN_MARGIN = 200
HEADER_BITS = 128
_MAGIC      = 0xEC401D00
_TERMINATOR = 0xFFFFFFFF
DECAY       = 0.6


def _ladder_for_sr(sr: int):
    return _LADDER_48K if sr >= 48000 else _LADDER_44K


def select_params(num_samples: int, sr: int, plaintext: str) -> Tuple[int, int, int]:
    enc_bytes         = _encrypted_byte_size(plaintext)
    total_bits_needed = HEADER_BITS + 32 + (4 + enc_bytes + 4) * 8 + 32
    ladder            = _ladder_for_sr(sr)

    for spb, d0, d1 in ladder:
        total_segs    = num_samples // spb
        if total_segs == 0:
            continue
        utilization   = total_bits_needed / total_segs
        free_segments = total_segs - total_bits_needed
        if utilization <= _MAX_UTIL and free_segments >= _MIN_MARGIN:
            return spb, d0, d1

    duration        = num_samples / sr
    min_spb         = ladder[0][0]
    min_segs_needed = int(total_bits_needed / _MAX_UTIL) + _MIN_MARGIN
    min_dur         = round(min_segs_needed * min_spb / sr, 1)
    raise ValueError(
        f"Audio too short for this message. "
        f"Duration: {duration:.1f}s @ {sr} Hz. "
        f"Need at least ~{min_dur}s of audio."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  BIT UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def _to_bits(data: bytes) -> str:
    return "".join(format(b, "08b") for b in data)


def _bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8:
        bits += "0" * (8 - len(bits) % 8)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


# ══════════════════════════════════════════════════════════════════════════════
#  CEPSTRUM DECODER
# ══════════════════════════════════════════════════════════════════════════════

def _decode_bit(segment: np.ndarray, d0: int, d1: int) -> str:
    n        = 2 ** int(np.ceil(np.log2(max(len(segment), d1 * 2 + 4))))
    windowed = segment.astype(np.float64) * np.hanning(len(segment))
    spec     = np.fft.rfft(windowed, n=n)
    cepstrum = np.fft.irfft(np.log(np.abs(spec) + 1e-10), n=n)
    half_w   = max(5, (d1 - d0) // 4)

    def peak(pos: int) -> float:
        lo = max(1, pos - half_w)
        hi = min(len(cepstrum), pos + half_w + 1)
        return float(np.max(np.abs(cepstrum[lo:hi]))) + 1e-10

    return "1" if peak(d1) > peak(d0) else "0"


def _decode_bits(samples: np.ndarray, spb: int, d0: int, d1: int,
                 start: int, count: int) -> str:
    bits = []
    for i in range(count):
        s   = start + i * spb
        e   = min(s + spb, len(samples))
        seg = samples[s:e] if s < len(samples) else np.array([])
        if len(seg) < spb:
            seg = np.pad(seg, (0, spb - len(seg)))
        bits.append(_decode_bit(seg, d0, d1) if s < len(samples) else "0")
    return "".join(bits)


# ══════════════════════════════════════════════════════════════════════════════
#  ECHO KERNEL
# ══════════════════════════════════════════════════════════════════════════════

def _make_kernel(delay: int, length: int) -> np.ndarray:
    k    = np.zeros(length, dtype=np.float64)
    k[0] = 1.0
    if 0 < delay < length:
        k[delay] += DECAY
    return k


# ══════════════════════════════════════════════════════════════════════════════
#  AUDIO I/O  (bytes in / bytes out — no temp files)
# ══════════════════════════════════════════════════════════════════════════════

import io

def _load_wav_bytes(data: bytes) -> Tuple[int, np.ndarray]:
    sr, raw = wavfile.read(io.BytesIO(data))
    if raw.dtype == np.int16:
        s = raw.astype(np.float64) / 32768.0
    elif raw.dtype == np.int32:
        s = raw.astype(np.float64) / 2_147_483_648.0
    else:
        s = raw.astype(np.float64)
    return sr, s.mean(axis=1) if s.ndim == 2 else s


def _save_wav_bytes(sr: int, samples: np.ndarray) -> bytes:
    buf = io.BytesIO()
    wavfile.write(buf, sr, (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16))
    buf.seek(0)
    return buf.read()


# ══════════════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def embed(audio_bytes: bytes, secret: str) -> Tuple[bytes, dict]:
    """
    Embed a secret message into WAV audio bytes.

    Returns:
        stego_bytes  : WAV bytes with embedded message
        params       : dict with spb, d0, d1, decay — store this for extraction
    """
    sr, samples = _load_wav_bytes(audio_bytes)
    spb, d0, d1 = select_params(len(samples), sr, secret)

    encrypted  = encrypt_message(secret)
    data_bytes = encrypted.encode("utf-8")
    data_len   = len(data_bytes)
    payload    = struct.pack(">I", data_len) + data_bytes + struct.pack(">I", _TERMINATOR)
    header     = struct.pack(">IIII", _MAGIC, spb, d0, d1)
    all_bits   = _to_bits(header) + _to_bits(payload)

    total_segs = len(samples) // spb
    avail_bits = max(0, total_segs - HEADER_BITS - 32 - 32)

    k0  = _make_kernel(d0, spb)
    k1  = _make_kernel(d1, spb)
    out = samples.copy()

    for i, bit in enumerate(all_bits):
        s = i * spb
        e = min(s + spb, len(samples))
        if s >= len(samples):
            break
        seg = samples[s:e]
        if len(seg) < spb:
            seg = np.pad(seg, (0, spb - len(seg)))
        conv     = fftconvolve(seg, k1 if bit == "1" else k0, mode="full")[:spb]
        out[s:e] = conv[:e - s]

    stego_bytes = _save_wav_bytes(sr, out)
    params      = {"spb": spb, "d0": d0, "d1": d1, "decay": DECAY}

    stats = {
        "sample_rate"    : sr,
        "duration_s"     : round(len(samples) / sr, 3),
        "parameters"     : params,
        "bits_embedded"  : len(all_bits),
        "bits_available" : avail_bits,
        "utilization_pct": round(len(all_bits) / total_segs * 100, 1),
        "original_chars" : len(secret),
        "encrypted_bytes": data_len,
    }

    return stego_bytes, params, stats


def extract(audio_bytes: bytes, params: dict) -> str:
    """
    Extract a secret message from stego WAV bytes.

    Args:
        audio_bytes : raw WAV bytes (the stego file)
        params      : dict with spb, d0, d1 — returned by embed()

    Returns:
        Decrypted plaintext message.
    """
    spb = params["spb"]
    d0  = params["d0"]
    d1  = params["d1"]

    sr, samples = _load_wav_bytes(audio_bytes)

    len_bits = _decode_bits(samples, spb, d0, d1, HEADER_BITS * spb, 32)
    data_len = struct.unpack(">I", _bits_to_bytes(len_bits))[0]

    max_bytes = max(0, (len(samples) // spb - HEADER_BITS - 32 - 32)) // 8
    if data_len <= 0 or data_len > max_bytes:
        raise ValueError(
            f"Decoded length {data_len} is invalid (max {max_bytes} bytes). "
            "Params may not match what was used during embedding."
        )

    data_start = (HEADER_BITS + 32) * spb
    data_bits  = _decode_bits(samples, spb, d0, d1, data_start, data_len * 8)
    data_bytes = _bits_to_bytes(data_bits)

    term_start = data_start + data_len * 8 * spb
    term_bits  = _decode_bits(samples, spb, d0, d1, term_start, 32)
    terminator = struct.unpack(">I", _bits_to_bytes(term_bits))[0]
    if terminator != _TERMINATOR:
        raise ValueError(
            f"Terminator mismatch (0x{terminator:08X}). "
            "Audio may be too short or params are incorrect."
        )

    return decrypt_message(data_bytes.decode("utf-8"))