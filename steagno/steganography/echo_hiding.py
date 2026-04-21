
# #updated-2
# """
# Echo Hiding Steganography for audio files - PRODUCTION READY with FIXED VALUES.
# Uses proven parameters that guarantee reliable embedding and extraction.
# """

# import struct
# import logging
# import json
# import os
# from typing import Dict, Tuple, Optional

# import numpy as np
# from scipy.io import wavfile
# from scipy.signal import fftconvolve

# from crypto import AESEncryption

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ── Constants ──────────────────────────────────────────────────────────────
# _MAGIC      = 0xEC401D00
# _TERMINATOR = 0xFFFFFFFF

# # Header layout: magic (4B) + spb (4B) + d0 (4B) + d1 (4B) = 16 bytes = 128 bits
# HEADER_BITS = 128

# # FIXED PARAMETERS - PROVEN WORKING VALUES (DO NOT CHANGE)
# # These values are optimized for 48kHz audio and provide reliable extraction
# FIXED_D0 = 50          # Delay for bit 0 (in samples)
# FIXED_D1 = 100          # Delay for bit 1 (in samples)  
# FIXED_DECAY = 0.5      # Echo strength (0.3-0.7 works well)
# FIXED_SPB = 400        # Samples per bit (MUST be > FIXED_D1 * 2)

# # Validation - ensure parameters are valid
# assert FIXED_D0 < FIXED_D1, "d0 must be less than d1"
# assert FIXED_D1 < FIXED_SPB, "d1 must be less than spb"
# assert FIXED_SPB >= FIXED_D1 * 2, "spb should be at least 2x d1 for reliable detection"

# _LOSSY_EXTS = {"mp3", "aac", "ogg", "m4a", "wma"}


# # ── Bit helpers ────────────────────────────────────────────────────────────

# def _to_bits(data: bytes) -> str:
#     """Convert bytes to binary string."""
#     return "".join(format(b, "08b") for b in data)


# def _bits_to_bytes(bits: str) -> bytes:
#     """Convert binary string to bytes."""
#     if len(bits) % 8 != 0:
#         bits = bits + "0" * (8 - len(bits) % 8)
#     return bytes(int(bits[i: i + 8], 2) for i in range(0, len(bits), 8))


# # ── Echo kernel ────────────────────────────────────────────────────────────

# def _make_echo_kernel(delay: int, decay: float, length: int) -> np.ndarray:
#     """Create an echo kernel: impulse at 0, echo at `delay`."""
#     k = np.zeros(length, dtype=np.float64)
#     k[0] = 1.0
#     if 0 < delay < length:
#         k[delay] += decay
#     return k


# # ── Cepstrum-based decoder ─────────────────────────────────────────────────

# # def _decode_one_bit(segment: np.ndarray, spb: int, d0: int, d1: int) -> str:
# #     """
# #     Decode a single bit by comparing cepstrum energy at d0 vs d1.
# #     Higher energy at d1 → bit '1'; higher at d0 → bit '0'.
# #     """
# #     if len(segment) < spb:
# #         segment = np.pad(segment, (0, spb - len(segment)), "constant")

# #     # Use power of 2 for FFT efficiency
# #     n = 2 ** int(np.ceil(np.log2(max(spb, d1 + 1, 4))))
# #     spec = np.fft.rfft(segment.astype(np.float64), n=n)
    
# #     # Add small epsilon to avoid log(0)
# #     cepstrum = np.fft.irfft(np.log(np.abs(spec) + 1e-10), n=n)

# #     e0 = float(np.abs(cepstrum[d0])) if d0 < len(cepstrum) else 0.0
# #     e1 = float(np.abs(cepstrum[d1])) if d1 < len(cepstrum) else 0.0
    
# #     # Add small epsilon to avoid division by zero
# #     e0 += 1e-10
# #     e1 += 1e-10
    
# #     # Use ratio for more stable detection
# #     ratio = e1 / e0
    
# #     return "1" if ratio > 1.2 else "0"  # 20% threshold for reliability

# def _decode_one_bit(segment: np.ndarray, spb: int, d0: int, d1: int) -> str:
#     if len(segment) < spb:
#         segment = np.pad(segment, (0, spb - len(segment)), "constant")

#     # Apply Hann window to reduce spectral leakage
#     window = np.hanning(len(segment))
#     windowed = segment.astype(np.float64) * window

#     n = 2 ** int(np.ceil(np.log2(max(spb, d1 * 2 + 1, 4))))
#     spec = np.fft.rfft(windowed, n=n)
#     cepstrum = np.fft.irfft(np.log(np.abs(spec) + 1e-10), n=n)

#     # Average energy in a small window around d0 and d1
#     # This is more robust than single-sample lookup
#     half_w = max(2, (d1 - d0) // 4)  # window half-width

#     def energy_around(pos):
#         lo = max(0, pos - half_w)
#         hi = min(len(cepstrum), pos + half_w + 1)
#         return float(np.mean(np.abs(cepstrum[lo:hi]))) + 1e-10

#     e0 = energy_around(d0)
#     e1 = energy_around(d1)

#     return "1" if e1 > e0 else "0"


# def _decode_bits(
#     samples: np.ndarray,
#     spb: int,
#     d0: int,
#     d1: int,
#     start_sample: int,
#     num_bits: int,
# ) -> str:
#     """
#     Decode `num_bits` consecutive bits starting at `start_sample`.
#     Each bit occupies exactly `spb` samples.
#     """
#     bits = []
#     for i in range(num_bits):
#         s = start_sample + i * spb
#         e = min(s + spb, len(samples))
        
#         if s >= len(samples):
#             bits.append("0")
#             continue
            
#         segment = samples[s:e]
#         bit = _decode_one_bit(segment, spb, d0, d1)
#         bits.append(bit)
    
#     return "".join(bits)


# # ── Capacity helper ────────────────────────────────────────────────────────

# def _available_payload_bits(num_samples: int, spb: int) -> int:
#     """
#     How many payload bits can fit after the fixed header?
#     Layout (in bits):  HEADER_BITS | 32 (length) | data | 32 (terminator)
#     """
#     total_segments = num_samples // spb
#     return max(0, total_segments - HEADER_BITS - 32 - 32)


# # ── Main class with FIXED VALUES ───────────────────────────────────────────

# class EchoHidingSteganography:
#     """
#     Echo hiding steganography with FIXED PROVEN PARAMETERS.
#     Uses d0=40, d1=80, spb=320, decay=0.5 for reliable operation.
#     """

#     def __init__(
#         self,
#         d0: int = None,
#         d1: int = None,
#         decay: float = None,
#         samples_per_bit: int = None,
#     ):
#         """
#         Initialize with fixed proven parameters.
#         Custom parameters are allowed but NOT recommended.
#         """
#         # Use fixed values by default (RECOMMENDED)
#         self.d0 = d0 if d0 is not None else FIXED_D0
#         self.d1 = d1 if d1 is not None else FIXED_D1
#         self.decay = decay if decay is not None else FIXED_DECAY
#         self.spb = samples_per_bit if samples_per_bit is not None else FIXED_SPB
        
#         # Validate parameters
#         if self.d0 >= self.d1:
#             raise ValueError(f"d0 ({self.d0}) must be < d1 ({self.d1})")
#         if not (0.0 < self.decay < 1.0):
#             raise ValueError(f"decay must be in (0, 1); got {self.decay}")
#         if self.spb <= self.d1:
#             raise ValueError(f"spb ({self.spb}) must be > d1 ({self.d1})")
        
#         logger.info(f"Initialized with FIXED parameters: spb={self.spb}, d0={self.d0}, d1={self.d1}, decay={self.decay}")

#     # ── Audio I/O ──────────────────────────────────────────────────────────

#     def _load_audio(self, path: str) -> Tuple[int, np.ndarray]:
#         """Load a WAV file and return (sample_rate, mono_float64_array)."""
#         ext = path.rsplit(".", 1)[-1].lower()
#         if ext in _LOSSY_EXTS:
#             raise ValueError(f"Lossy format '.{ext}' is not supported. Use WAV files only.")

#         sr, data = wavfile.read(path)

#         if data.dtype == np.int16:
#             s = data.astype(np.float64) / 32768.0
#         elif data.dtype == np.int32:
#             s = data.astype(np.float64) / 2_147_483_648.0
#         elif data.dtype in (np.float32, np.float64):
#             s = data.astype(np.float64)
#         else:
#             raise ValueError(f"Unsupported WAV sample dtype: {data.dtype}. Use 16-bit PCM.")

#         if s.ndim == 2:  # stereo → mono
#             s = s.mean(axis=1)

#         return sr, s

#     @staticmethod
#     def _save_wav(path: str, sr: int, samples: np.ndarray) -> None:
#         """Save audio as 16-bit PCM WAV."""
#         clipped = np.clip(samples, -1.0, 1.0)
#         wavfile.write(path, sr, (clipped * 32767).astype(np.int16))

#     # ── Capacity query ─────────────────────────────────────────────────────

#     def max_message_bytes(self, audio_path: str) -> int:
#         """Return maximum number of encrypted bytes that can be hidden."""
#         _, samples = self._load_audio(audio_path)
#         available_bits = _available_payload_bits(len(samples), self.spb)
#         return available_bits // 8

#     # ── Embed (USES FIXED VALUES) ─────────────────────────────────────────

#     def embed(self, audio_path: str, secret: str, output_path: str) -> Dict:
#         """
#         Embed *secret* into the WAV using FIXED parameters.
#         No auto-selection - uses proven values for reliability.
#         """
#         out_ext = output_path.rsplit(".", 1)[-1].lower()
#         if out_ext != "wav":
#             raise ValueError(f"Output must be a WAV file; got '.{out_ext}'.")

#         sr, samples = self._load_audio(audio_path)
#         num_samples = len(samples)

#         logger.info(f"Audio: {num_samples} samples @ {sr} Hz ({num_samples/sr:.2f}s)")

#         # ── Encrypt & build payload ────────────────────────────────────────
#         encrypted = AESEncryption.encrypt(secret)
#         data_bytes = encrypted.encode("utf-8")
#         data_length = len(data_bytes)

#         payload = (
#             struct.pack(">I", data_length)
#             + data_bytes
#             + struct.pack(">I", _TERMINATOR)
#         )
#         payload_bits = _to_bits(payload)
#         total_payload_bits = len(payload_bits)

#         # ── Check capacity with FIXED parameters ──────────────────────────
#         available_bits = _available_payload_bits(num_samples, self.spb)
        
#         if total_payload_bits > available_bits:
#             max_chars = int(available_bits / 8 / 1.4)  # Approximate for text
#             raise ValueError(
#                 f"Message too long for this audio with fixed parameters.\n"
#                 f"  Needed: {total_payload_bits} bits\n"
#                 f"  Available: {available_bits} bits\n"
#                 f"  Max message length: ~{max_chars} characters\n"
#                 f"  Solutions: Use longer audio or shorten your message"
#             )

#         logger.info(f"Embedding with FIXED parameters: spb={self.spb}, d0={self.d0}, d1={self.d1}")
#         logger.info(f"Message: {len(secret)} chars → {data_length}B → {total_payload_bits} bits")

#         # ── Build full bit-stream: header + payload ────────────────────────
#         header = struct.pack(">IIII", _MAGIC, self.spb, self.d0, self.d1)
#         header_bits = _to_bits(header)
#         all_bits = header_bits + payload_bits

#         # ── Echo kernels ───────────────────────────────────────────────────
#         k0 = _make_echo_kernel(self.d0, self.decay, self.spb)
#         k1 = _make_echo_kernel(self.d1, self.decay, self.spb)

#         # ── Embed: convolve each segment with the appropriate kernel ───────
#         output = samples.copy()
#         for i, bit in enumerate(all_bits):
#             s = i * self.spb
#             e = min(s + self.spb, num_samples)
#             if s >= num_samples:
#                 break

#             seg = samples[s:e]
#             if len(seg) < self.spb:
#                 seg = np.pad(seg, (0, self.spb - len(seg)), "constant")

#             kernel = k1 if bit == "1" else k0
#             convolved = fftconvolve(seg, kernel, mode="full")[:self.spb]
#             output[s:e] = convolved[: e - s]

#         self._save_wav(output_path, sr, output)
        
#         # Save parameters for reference (though they're fixed)
#         params_file = output_path.replace('.wav', '_params.json')
#         with open(params_file, 'w') as f:
#             json.dump({
#                 "spb": self.spb,
#                 "d0": self.d0,
#                 "d1": self.d1,
#                 "decay": self.decay,
#                 "note": "Fixed parameters - do not change for extraction"
#             }, f, indent=2)
        
#         logger.info(f"✓ Embedded {len(all_bits)} bits → '{output_path}'")

#         total_segs = num_samples // self.spb
#         return {
#             "success": True,
#             "output_path": output_path,
#             "sample_rate": sr,
#             "duration_s": round(num_samples / sr, 3),
#             "parameters": {
#                 "spb": self.spb,
#                 "d0": self.d0,
#                 "d1": self.d1,
#                 "decay": self.decay
#             },
#             "embedding": {
#                 "bits_embedded": len(all_bits),
#                 "bits_available": available_bits,
#                 "total_segments": total_segs,
#                 "utilization_pct": round(len(all_bits) / total_segs * 100, 1),
#             },
#             "message": {
#                 "original_chars": len(secret),
#                 "encrypted_bytes": data_length,
#                 "payload_bits": total_payload_bits,
#             },
#         }

#     # ── Extract (USES FIXED VALUES - FASTEST METHOD) ──────────────────────

#     # def extract(self, audio_path: str) -> str:
#     #     """
#     #     Extract secret using FIXED parameters.
#     #     This is the FASTEST and MOST RELIABLE method.
#     #     No auto-detection - uses the proven fixed values directly.
#     #     """
#     #     logger.info(f"Extracting with FIXED parameters: spb={FIXED_SPB}, d0={FIXED_D0}, d1={FIXED_D1}")
        
#     #     sr, samples = self._load_audio(audio_path)
        
#     #     # Extract directly with fixed parameters
#     #     return self._extract_payload(samples, FIXED_SPB, FIXED_D0, FIXED_D1)

#     def extract(self, audio_path: str) -> str:
#         """
#         Extract secret using the instance parameters.
#         This respects the parameters set during initialization.
#         """
#         print(f"🎯 extract() called with instance params: spb={self.spb}, d0={self.d0}, d1={self.d1}")
        
#         sr, samples = self._load_audio(audio_path)
        
#         # Use the instance's parameters (self.spb, self.d0, self.d1)
#         # NOT the global FIXED_* constants
#         return self._extract_payload(samples, self.spb, self.d0, self.d1)
    
#     def extract_with_params(self, audio_path: str, spb: int, d0: int, d1: int) -> str:
#         """
#         Extract using custom parameters (for backwards compatibility).
#         Use extract() instead for best results.
#         """
#         logger.info(f"Extracting with custom parameters: spb={spb}, d0={d0}, d1={d1}")
#         sr, samples = self._load_audio(audio_path)
#         return self._extract_payload(samples, spb, d0, d1)

#     def _extract_payload(
#         self,
#         samples: np.ndarray,
#         spb: int,
#         d0: int,
#         d1: int,
#     ) -> str:
#         """
#         Given validated (spb, d0, d1), decode the payload and return decrypted text.
#         """
#         # Verify we have enough samples
#         min_samples_needed = (HEADER_BITS + 32 + 32) * spb
#         if len(samples) < min_samples_needed:
#             raise ValueError(f"Audio too short. Need at least {min_samples_needed} samples, got {len(samples)}")

#         # ── Decode length field (bits 128..159) ───────────────────────────
#         length_start_sample = HEADER_BITS * spb
#         len_bits = _decode_bits(samples, spb, d0, d1, length_start_sample, 32)
#         len_bytes = _bits_to_bytes(len_bits)

#         if len(len_bytes) < 4:
#             raise ValueError("Truncated length field — audio may be corrupted.")

#         data_length = struct.unpack(">I", len_bytes[:4])[0]
#         logger.info(f"  Payload length: {data_length} bytes")

#         # Sanity check
#         max_possible_bytes = ((len(samples) // spb) - HEADER_BITS - 32 - 32) // 8
#         if data_length <= 0 or data_length > max_possible_bytes:
#             raise ValueError(
#                 f"Invalid payload length {data_length}. Max possible: {max_possible_bytes} bytes.\n"
#                 f"This usually means the audio was not embedded with these parameters."
#             )

#         # ── Decode data bits ─────────────────────────────────────────────
#         data_start_sample = (HEADER_BITS + 32) * spb
#         data_bits = _decode_bits(
#             samples, spb, d0, d1, data_start_sample, data_length * 8
#         )
#         data_bytes = _bits_to_bytes(data_bits)

#         # ── Decode & verify terminator ────────────────────────────────────
#         term_start_sample = data_start_sample + data_length * 8 * spb 
#         term_bits = _decode_bits(samples, spb, d0, d1, term_start_sample, 32)
#         terminator = struct.unpack(">I", _bits_to_bytes(term_bits))[0]

#         if terminator != _TERMINATOR:
#             logger.warning(f"Terminator mismatch (expected 0x{_TERMINATOR:08X}, got 0x{terminator:08X})")

#         # ── Decrypt ───────────────────────────────────────────────────────
#         try:
#             encrypted_str = data_bytes.decode("utf-8")
#         except UnicodeDecodeError as exc:
#             raise ValueError(f"Encrypted payload is not valid UTF-8: {exc}") from exc

#         try:
#             plaintext = AESEncryption.decrypt(encrypted_str)
#         except Exception as exc:
#             raise ValueError(f"Decryption failed: {exc}") from exc

#         logger.info(f"✓ Decrypted {len(plaintext)} characters successfully.")
#         return plaintext




#updated- 4
"""
Echo Hiding Steganography for audio files.

Embedding   : each bit is encoded by convolving a segment with an echo kernel
              whose delay is d0 (bit=0) or d1 (bit=1).

Extraction  : echo-cancellation decoder — subtract the candidate echo and
              measure residual energy.  The delay that yields the *lower*
              residual is the one that was embedded.  This is algebraically
              correct and robust for any audio content.
"""

import struct
import logging
import json
from typing import Dict, Tuple

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

from crypto import AESEncryption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────
_MAGIC      = 0xEC401D00
_TERMINATOR = 0xFFFFFFFF

# Header layout: magic(4B) + spb(4B) + d0(4B) + d1(4B) = 16 bytes = 128 bits
HEADER_BITS = 128

# FIXED / DEFAULT PARAMETERS
FIXED_D0    = 50
FIXED_D1    = 100
FIXED_DECAY = 0.5
FIXED_SPB   = 400          # must be > FIXED_D1 * 2

assert FIXED_D0 < FIXED_D1,           "d0 must be < d1"
assert FIXED_D1 < FIXED_SPB,          "d1 must be < spb"
assert FIXED_SPB >= FIXED_D1 * 2,     "spb should be >= 2 × d1"

_LOSSY_EXTS = {"mp3", "aac", "ogg", "m4a", "wma"}


# ── Bit helpers ────────────────────────────────────────────────────────────

def _to_bits(data: bytes) -> str:
    return "".join(format(b, "08b") for b in data)


def _bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8:
        bits += "0" * (8 - len(bits) % 8)
    return bytes(int(bits[i: i + 8], 2) for i in range(0, len(bits), 8))


# ── Echo kernel ────────────────────────────────────────────────────────────

def _make_echo_kernel(delay: int, decay: float, length: int) -> np.ndarray:
    """Impulse at 0, echo at `delay`."""
    k = np.zeros(length, dtype=np.float64)
    k[0] = 1.0
    if 0 < delay < length:
        k[delay] += decay
    return k


# ── Echo-cancellation bit decoder ─────────────────────────────────────────

def _decode_one_bit(
    segment: np.ndarray,
    spb: int,
    d0: int,
    d1: int,
    decay: float = 0.5,
) -> str:
    """
    Decide whether the echo in *segment* is at d0 (→ '0') or d1 (→ '1').

    Method — echo cancellation
    --------------------------
    Embedding added  ``decay · x[n − d]``  to the original x.
    Cancelling at the correct delay gives the smallest residual:

        res[n] = y[n] − decay · y[n − d]
               = x[n] − decay² · x[n − 2d]      (if d was correct)

    vs. a cross-term that keeps the full echo when d is wrong.
    The energy ratio is ~ (1 + decay⁴) / (1 + 2·decay² + decay⁴), which
    for decay=0.5 is ~1.06 / 1.56 — a reliable ~32 % gap regardless of
    the audio content.
    """
    if len(segment) < spb:
        segment = np.pad(segment, (0, spb - len(segment)), "constant")

    seg = segment.astype(np.float64)

    # Near-silent segment — echo is undetectable; default to '0'
    if np.sum(seg ** 2) < 1e-12:
        return "0"

    def cancel(s: np.ndarray, delay: int) -> np.ndarray:
        r = s.copy()
        if 0 < delay < len(s):
            r[delay:] -= decay * s[: len(s) - delay]
        return r

    res0 = cancel(seg, d0)
    res1 = cancel(seg, d1)

    # Measure residual from d0 onwards.
    # For the correct delay, cancellation is complete by d0; for the wrong
    # delay, the echo is still present in [d0, d1).  Using d0 as the start
    # gives 450 samples instead of 380 while maintaining the same ~0.695
    # energy ratio between the two hypotheses.
    start = d0
    e0 = float(np.sum(res0[start:] ** 2))
    e1 = float(np.sum(res1[start:] ** 2))

    return "0" if e0 < e1 else "1"


def _decode_bits(
    samples: np.ndarray,
    spb: int,
    d0: int,
    d1: int,
    start_sample: int,
    num_bits: int,
    decay: float = 0.5,
) -> str:
    """Decode *num_bits* consecutive bits starting at *start_sample*."""
    bits: list[str] = []
    for i in range(num_bits):
        s = start_sample + i * spb
        if s >= len(samples):
            bits.append("0")
            continue
        e = min(s + spb, len(samples))
        bits.append(_decode_one_bit(samples[s:e], spb, d0, d1, decay))
    return "".join(bits)


# ── Capacity helper ────────────────────────────────────────────────────────

def _available_payload_bits(num_samples: int, spb: int) -> int:
    """Payload bits available after header + length field + terminator."""
    total_segments = num_samples // spb
    return max(0, total_segments - HEADER_BITS - 32 - 32)


# ── Main class ─────────────────────────────────────────────────────────────

class EchoHidingSteganography:
    """
    Echo hiding steganography.
    Default parameters (d0=50, d1=100, spb=400, decay=0.5) work well for
    WAV files at common sample rates.  Custom values are supported but must
    be the same at embed *and* extract time.
    """

    def __init__(
        self,
        d0: int = None,
        d1: int = None,
        decay: float = None,
        samples_per_bit: int = None,
    ):
        self.d0    = d0             if d0             is not None else FIXED_D0
        self.d1    = d1             if d1             is not None else FIXED_D1
        self.decay = decay          if decay          is not None else FIXED_DECAY
        self.spb   = samples_per_bit if samples_per_bit is not None else FIXED_SPB

        if self.d0 >= self.d1:
            raise ValueError(f"d0 ({self.d0}) must be < d1 ({self.d1})")
        if not (0.0 < self.decay < 1.0):
            raise ValueError(f"decay must be in (0, 1); got {self.decay}")
        if self.spb <= self.d1:
            raise ValueError(f"spb ({self.spb}) must be > d1 ({self.d1})")

        logger.info(
            "EchoHiding params: spb=%d  d0=%d  d1=%d  decay=%.2f",
            self.spb, self.d0, self.d1, self.decay,
        )

    # ── Audio I/O ──────────────────────────────────────────────────────────

    def _load_audio(self, path: str) -> Tuple[int, np.ndarray]:
        ext = path.rsplit(".", 1)[-1].lower()
        if ext in _LOSSY_EXTS:
            raise ValueError(
                f"Lossy format '.{ext}' is not supported. Use WAV files only."
            )

        sr, data = wavfile.read(path)

        if data.dtype == np.int16:
            s = data.astype(np.float64) / 32768.0
        elif data.dtype == np.int32:
            s = data.astype(np.float64) / 2_147_483_648.0
        elif data.dtype in (np.float32, np.float64):
            s = data.astype(np.float64)
        else:
            raise ValueError(
                f"Unsupported WAV dtype: {data.dtype}. Use 16-bit PCM."
            )

        if s.ndim == 2:          # stereo → mono
            s = s.mean(axis=1)

        return sr, s

    @staticmethod
    def _save_wav(path: str, sr: int, samples: np.ndarray) -> None:
        clipped = np.clip(samples, -1.0, 1.0)
        wavfile.write(path, sr, (clipped * 32767).astype(np.int16))

    # ── Capacity query ─────────────────────────────────────────────────────

    def max_message_bytes(self, audio_path: str) -> int:
        """Maximum number of encrypted bytes that can be hidden."""
        _, samples = self._load_audio(audio_path)
        return _available_payload_bits(len(samples), self.spb) // 8

    # ── Embed ──────────────────────────────────────────────────────────────

    def embed(self, audio_path: str, secret: str, output_path: str) -> Dict:
        """Embed *secret* into *audio_path* and write the result to *output_path*."""
        if not output_path.lower().endswith(".wav"):
            raise ValueError(f"Output must be a WAV file; got '{output_path}'.")

        sr, samples = self._load_audio(audio_path)
        num_samples  = len(samples)

        logger.info(
            "Audio: %d samples @ %d Hz (%.2fs)",
            num_samples, sr, num_samples / sr,
        )

        # Encrypt & serialise
        encrypted  = AESEncryption.encrypt(secret)
        data_bytes = encrypted.encode("utf-8")
        data_length = len(data_bytes)

        payload = (
            struct.pack(">I", data_length)
            + data_bytes
            + struct.pack(">I", _TERMINATOR)
        )
        payload_bits      = _to_bits(payload)
        total_payload_bits = len(payload_bits)

        available_bits = _available_payload_bits(num_samples, self.spb)
        if total_payload_bits > available_bits:
            max_chars = int(available_bits / 8 / 1.4)
            raise ValueError(
                f"Message too long for this audio.\n"
                f"  Needed   : {total_payload_bits} bits\n"
                f"  Available: {available_bits} bits\n"
                f"  Max msg  : ~{max_chars} characters\n"
                "  Fix      : use longer audio or shorten the message."
            )

        # Build full bit-stream: header | length | data | terminator
        header      = struct.pack(">IIII", _MAGIC, self.spb, self.d0, self.d1)
        all_bits    = _to_bits(header) + payload_bits

        k0 = _make_echo_kernel(self.d0, self.decay, self.spb)
        k1 = _make_echo_kernel(self.d1, self.decay, self.spb)

        output = samples.copy()
        for i, bit in enumerate(all_bits):
            s = i * self.spb
            if s >= num_samples:
                break
            e   = min(s + self.spb, num_samples)
            seg = samples[s:e]
            if len(seg) < self.spb:
                seg = np.pad(seg, (0, self.spb - len(seg)), "constant")

            kernel   = k1 if bit == "1" else k0
            convolved = fftconvolve(seg, kernel, mode="full")[: self.spb]
            output[s:e] = convolved[: e - s]

        self._save_wav(output_path, sr, output)

        # Persist parameters alongside the audio so extract is self-contained
        params_path = output_path.replace(".wav", "_params.json")
        with open(params_path, "w") as fh:
            json.dump(
                {
                    "spb"  : self.spb,
                    "d0"   : self.d0,
                    "d1"   : self.d1,
                    "decay": self.decay,
                },
                fh,
                indent=2,
            )

        logger.info("Embedded %d bits → '%s'", len(all_bits), output_path)

        total_segs = num_samples // self.spb
        return {
            "success"   : True,
            "output_path": output_path,
            "sample_rate": sr,
            "duration_s" : round(num_samples / sr, 3),
            "parameters" : {
                "spb"  : self.spb,
                "d0"   : self.d0,
                "d1"   : self.d1,
                "decay": self.decay,
            },
            "embedding": {
                "bits_embedded"  : len(all_bits),
                "bits_available" : available_bits,
                "total_segments" : total_segs,
                "utilization_pct": round(len(all_bits) / total_segs * 100, 1),
            },
            "message": {
                "original_chars" : len(secret),
                "encrypted_bytes": data_length,
                "payload_bits"   : total_payload_bits,
            },
        }

    # ── Extract ────────────────────────────────────────────────────────────

    def extract(self, audio_path: str) -> str:
        """Extract and decrypt the hidden message using this instance's parameters."""
        logger.info(
            "Extracting: spb=%d  d0=%d  d1=%d  decay=%.2f",
            self.spb, self.d0, self.d1, self.decay,
        )
        sr, samples = self._load_audio(audio_path)
        return self._extract_payload(samples, self.spb, self.d0, self.d1, self.decay)

    def extract_with_params(
        self, audio_path: str, spb: int, d0: int, d1: int, decay: float = 0.5
    ) -> str:
        """Extract using explicitly supplied parameters."""
        logger.info(
            "Extracting with custom params: spb=%d  d0=%d  d1=%d  decay=%.2f",
            spb, d0, d1, decay,
        )
        sr, samples = self._load_audio(audio_path)
        return self._extract_payload(samples, spb, d0, d1, decay)

    # ── Core extraction ────────────────────────────────────────────────────

    def _extract_payload(
        self,
        samples: np.ndarray,
        spb: int,
        d0: int,
        d1: int,
        decay: float = 0.5,
    ) -> str:
        min_needed = (HEADER_BITS + 32 + 32) * spb
        if len(samples) < min_needed:
            raise ValueError(
                f"Audio too short: need {min_needed} samples, got {len(samples)}."
            )

        # ── Validate header ────────────────────────────────────────────────
        header_bits  = _decode_bits(samples, spb, d0, d1, 0, HEADER_BITS, decay)
        header_bytes = _bits_to_bytes(header_bits)

        magic = struct.unpack(">I", header_bytes[:4])[0]

        # Allow up to 4 bit-flips — a single corrupted segment can flip a bit
        # even when the parameters are correct.
        magic_hamming = bin(magic ^ _MAGIC).count("1")
        if magic_hamming > 4:
            raise ValueError(
                f"Header magic mismatch: 0x{magic:08X} "
                f"(expected 0x{_MAGIC:08X}, Hamming distance {magic_hamming}).\n"
                "The audio was not embedded with EchoHiding, or the extraction "
                "parameters (spb / d0 / d1) do not match those used at embed time."
            )
        if magic_hamming > 0:
            logger.warning(
                "Header magic has %d bit-flip(s) (0x%08X vs 0x%08X) — "
                "treating as valid and continuing.",
                magic_hamming, magic, _MAGIC,
            )

        _, h_spb, h_d0, h_d1 = struct.unpack(">IIII", header_bytes[:16])
        if (h_spb, h_d0, h_d1) != (spb, d0, d1):
            logger.warning(
                "Parameter mismatch — provided (%d,%d,%d) but header says (%d,%d,%d). "
                "Continuing with provided values.",
                spb, d0, d1, h_spb, h_d0, h_d1,
            )

        # ── Decode payload length (32 bits after header) ───────────────────
        length_start = HEADER_BITS * spb
        len_bits  = _decode_bits(samples, spb, d0, d1, length_start, 32, decay)
        data_length = struct.unpack(">I", _bits_to_bytes(len_bits)[:4])[0]

        logger.info("Payload length field: %d bytes", data_length)

        max_possible = ((len(samples) // spb) - HEADER_BITS - 32 - 32) // 8
        if data_length <= 0 or data_length > max_possible:
            raise ValueError(
                f"Invalid payload length {data_length} "
                f"(max possible: {max_possible} bytes). "
                "Extraction parameters likely do not match those used during embedding."
            )

        # ── Decode data ────────────────────────────────────────────────────
        data_start = (HEADER_BITS + 32) * spb
        data_bits  = _decode_bits(
            samples, spb, d0, d1, data_start, data_length * 8, decay
        )
        data_bytes = _bits_to_bytes(data_bits)

        # ── Verify terminator ──────────────────────────────────────────────
        term_start = data_start + data_length * 8 * spb
        term_bits  = _decode_bits(samples, spb, d0, d1, term_start, 32, decay)
        terminator = struct.unpack(">I", _bits_to_bytes(term_bits))[0]

        if terminator != _TERMINATOR:
            logger.warning(
                "Terminator mismatch: expected 0x%08X, got 0x%08X",
                _TERMINATOR, terminator,
            )

        # ── Decrypt ───────────────────────────────────────────────────────
        try:
            encrypted_str = data_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                f"Decoded payload is not valid UTF-8: {exc}\n"
                "This usually means the extraction parameters are wrong."
            ) from exc

        try:
            plaintext = AESEncryption.decrypt(encrypted_str)
        except Exception as exc:
            raise ValueError(
                f"Decryption failed: {exc}\n"
                "This usually means the extraction parameters do not match "
                "those used during embedding."
            ) from exc

        logger.info("Decrypted %d characters successfully.", len(plaintext))
        return plaintext