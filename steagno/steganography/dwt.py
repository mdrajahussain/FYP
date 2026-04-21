

# """
# DWT (Discrete Wavelet Transform) Steganography for images.

# One bit is stored per coefficient in the LL sub-band of a single-level
# Haar DWT by nudging the LSB of the quantised coefficient:
#     quantised coefficient is even  →  bit 0
#     quantised coefficient is odd   →  bit 1

# Wire format is identical to the DCT/LSB modules:
#     [4-byte big-endian length][encrypted data][4-byte 0xFFFFFFFF terminator]

# Shape-stability guarantee
# -------------------------
# This module uses pywt mode='periodization', which gives:

#     cA.shape == (ceil(h/2), ceil(w/2))   ← always exactly half, no overshoot
#     idwt2(..., mode='periodization')     ← returns exactly (h, w), no padding

# This eliminates ALL shape-mismatch errors regardless of whether the image
# has odd or even dimensions.  No manual padding is needed.

# Quantisation step
# -----------------
# Default is 64.  Haar LL coefficients are sums of 2×2 pixel blocks so a
# ±0.5 uint8 rounding error propagates as ±2 in the float coefficient domain.
# With step=64, that error is only ±2/64 ≈ 0.03 — np.round will never
# misclassify the LSB.  Do not go below 8 without testing on your images.

# Lossless output only
# --------------------
# JPEG recompression will corrupt the payload.  The module raises ValueError
# if a lossy output extension is requested.
# """

# import struct
# import warnings
# from typing import Dict

# import cv2
# import numpy as np
# import pywt  # pip install PyWavelets

# from crypto import AESEncryption


# _TERMINATOR         = 0xFFFFFFFF
# _LOSSY_EXTS         = {"jpg", "jpeg"}
# _DEFAULT_QUANT_STEP = 64
# _WAVELET            = "haar"
# _MODE               = "periodization"   # key: guarantees idwt2 returns exact (h, w)


# # ---------------------------------------------------------------------------
# # Bit-level helpers
# # ---------------------------------------------------------------------------

# def _to_bits(data: bytes) -> str:
#     return "".join(format(b, "08b") for b in data)


# def _bits_to_bytes(bits: str) -> bytes:
#     return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


# # ---------------------------------------------------------------------------
# # Main class
# # ---------------------------------------------------------------------------

# class DWTSteganography:
#     """Embed / extract secrets via single-level Haar DWT coefficient LSBs."""

#     # ------------------------------------------------------------------
#     # embed
#     # ------------------------------------------------------------------
#     @staticmethod
#     def embed(
#         image_path: str,
#         secret: str,
#         output_path: str,
#         quantisation_step: int = _DEFAULT_QUANT_STEP,
#     ) -> Dict:
#         """
#         Embed *secret* into *image_path* and write the result to *output_path*.

#         Parameters
#         ----------
#         image_path        : Path to the carrier image (any OpenCV-readable format).
#         secret            : Plaintext message to hide.
#         output_path       : Destination — must be lossless (PNG / BMP / TIFF).
#         quantisation_step : Robustness vs. visibility trade-off.
#                             Must match the value used during extraction.
#                             Default 64 is safe for standard uint8 PNG images.
#         """
#         # ---- Guard: refuse lossy output --------------------------------
#         ext = output_path.rsplit(".", 1)[-1].lower()
#         if ext in _LOSSY_EXTS:
#             raise ValueError(
#                 f"DWT steganography requires a lossless output format. "
#                 f"'{ext}' is lossy and will destroy the payload. "
#                 "Use .png, .bmp, or .tiff instead."
#             )

#         if quantisation_step < 2:
#             raise ValueError(
#                 f"quantisation_step must be >= 2; got {quantisation_step}."
#             )

#         # ---- Load as grayscale ----------------------------------------
#         img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#         if img is None:
#             bgr = cv2.imread(image_path)
#             if bgr is None:
#                 raise ValueError(f"Cannot open image: {image_path}")
#             img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

#         # Store original dtype for later
#         original_dtype = img.dtype
#         h, w = img.shape

#         # ---- Single-level Haar DWT with periodization -----------------
#         # mode='periodization' guarantees:
#         #   cA.shape == (ceil(h/2), ceil(w/2))
#         #   idwt2 output == exactly (h, w)   ← no shape mismatch possible
#         cA, (cH, cV, cD) = pywt.dwt2(
#             img.astype(np.float64), _WAVELET, mode=_MODE
#         )

#         # Quantise LL sub-band
#         cA_q = np.round(cA / quantisation_step).astype(np.int64)
#         num_coeffs = cA_q.size

#         # ---- Build payload --------------------------------------------
#         encrypted   = AESEncryption.encrypt(secret)
#         data_bytes  = encrypted.encode("utf-8")
#         data_length = len(data_bytes)

#         payload = (
#             struct.pack(">I", data_length)
#             + data_bytes
#             + struct.pack(">I", _TERMINATOR)
#         )
#         bits       = _to_bits(payload)
#         total_bits = len(bits)

#         if total_bits > num_coeffs:
#             raise ValueError(
#                 f"Message too large for DWT: needs {total_bits} coefficients, "
#                 f"LL sub-band only has {num_coeffs}. "
#                 "Use a larger image or a shorter message."
#             )

#         # ---- Embed bits via LSB flip of quantised coefficients ---------
#         flat = cA_q.flatten()
#         for i, bit in enumerate(bits):
#             if bit == "1":
#                 flat[i] = flat[i] | np.int64(1)
#             else:
#                 flat[i] = flat[i] & ~np.int64(1)

#         # Important: Use exact multiplication and rounding
#         cA_modified = (flat.reshape(cA_q.shape) * quantisation_step).astype(
#             np.float64
#         )

#         # ---- Inverse DWT ----------------------------------------------
#         # With mode='periodization' this is guaranteed to return (h, w).
#         reconstructed = pywt.idwt2(
#             (cA_modified, (cH, cV, cD)), _WAVELET, mode=_MODE
#         )

#         # Defensive check — should never fire with periodization
#         rh, rw = reconstructed.shape
#         if (rh, rw) != (h, w):
#             raise RuntimeError(
#                 f"IDWT returned unexpected shape {reconstructed.shape} "
#                 f"(expected {img.shape}). "
#                 "This should not happen with mode='periodization'."
#             )

#         # Clip and convert back to original dtype
#         result = np.clip(reconstructed, 0, 255).astype(original_dtype)
        
#         # Save as PNG to preserve exact pixel values
#         cv2.imwrite(output_path, result)

#         return {
#             "algorithm"         : "DWT",
#             "wavelet"           : _WAVELET,
#             "mode"              : _MODE,
#             "quantisation_step" : quantisation_step,
#             "bits_embedded"     : total_bits,
#             "total_coefficients": num_coeffs,
#             "encrypted_length"  : data_length,
#             "image_size"        : f"{w}x{h}",
#         }

#     # ------------------------------------------------------------------
#     # extract
#     # ------------------------------------------------------------------
#     @staticmethod
#     def extract(
#         image_path: str,
#         quantisation_step: int = _DEFAULT_QUANT_STEP,
#     ) -> str:
#         """
#         Recover and decrypt the secret previously embedded in *image_path*.

#         *quantisation_step* MUST match the value used during embedding.
#         """
#         # Read image exactly as it was saved (grayscale)
#         img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#         if img is None:
#             # Try reading as BGR and convert
#             bgr = cv2.imread(image_path)
#             if bgr is None:
#                 raise ValueError(f"Cannot open image: {image_path}")
#             img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

#         # Ensure float64 for consistent DWT computation
#         img_float = img.astype(np.float64)

#         # ---- Single-level Haar DWT with periodization -----------------
#         # CRITICAL: We must decompose the image exactly as in embedding
#         cA, (cH, cV, cD) = pywt.dwt2(img_float, _WAVELET, mode=_MODE)

#         # Re-quantise using the same step as embedding
#         cA_q = np.round(cA / quantisation_step).astype(np.int64)
#         flat = cA_q.flatten()

#         # ---- Extract raw bits from LSBs --------------------------------
#         raw_bits = "".join(str(int(v) & 1) for v in flat)

#         if len(raw_bits) < 32:
#             raise ValueError("Not enough DWT coefficients for a length header.")

#         # ---- Parse wire format ----------------------------------------
#         # Extract length header (first 32 bits = 4 bytes)
#         try:
#             length_bytes = _bits_to_bytes(raw_bits[:32])
#             data_length = struct.unpack(">I", length_bytes)[0]
#         except Exception as exc:
#             raise ValueError(f"Failed to parse length header: {exc}")

#         # Validate data_length
#         if data_length <= 0 or data_length > 10000000:  # Sanity check: 10MB max
#             raise ValueError(
#                 f"DWT: Invalid data length {data_length}. "
#                 "Likely causes: wrong quantisation_step, or no data hidden."
#             )

#         # Calculate required bits for the data
#         data_bits_needed = data_length * 8
#         terminator_bits_needed = 32  # 4 bytes = 32 bits
#         total_bits_needed = 32 + data_bits_needed + terminator_bits_needed

#         if len(raw_bits) < total_bits_needed:
#             raise ValueError(
#                 f"DWT: Not enough coefficients. Need {total_bits_needed} bits, "
#                 f"but only have {len(raw_bits)}. "
#                 "Likely causes: wrong quantisation_step or image was modified."
#             )

#         # Extract data bits
#         data_start = 32
#         data_end = data_start + data_bits_needed
#         data_bits = raw_bits[data_start:data_end]
#         data_bytes = _bits_to_bytes(data_bits)

#         # Extract and verify terminator
#         term_start = data_end
#         term_end = term_start + 32
#         term_bits = raw_bits[term_start:term_end]
        
#         try:
#             terminator = struct.unpack(">I", _bits_to_bytes(term_bits))[0]
#         except Exception as exc:
#             raise ValueError(f"Failed to parse terminator: {exc}")

#         if terminator != _TERMINATOR:
#             raise ValueError(
#                 f"DWT terminator mismatch (got 0x{terminator:08X}). "
#                 "Most likely causes:\n"
#                 f"  1. quantisation_step mismatch between embed and extract.\n"
#                 "  2. Image was re-saved through a lossy format (JPEG/WebP).\n"
#                 f"  3. quantisation_step too small — try a larger value "
#                 f"(current: {quantisation_step}, recommended default: "
#                 f"{_DEFAULT_QUANT_STEP}).\n"
#                 "  4. No hidden data in this image."
#             )

#         # ---- Decode and decrypt ---------------------------------------
#         try:
#             encrypted_str = data_bytes.decode("utf-8")
#         except UnicodeDecodeError as exc:
#             raise ValueError(f"DWT: UTF-8 decode failed: {exc}") from exc

#         try:
#             return AESEncryption.decrypt(encrypted_str)
#         except Exception as exc:
#             raise ValueError(f"DWT: AES decryption failed: {exc}") from exc



# update


"""
DWT (Discrete Wavelet Transform) Steganography for images.

One bit is stored per coefficient in the LL sub-band of a single-level
Haar DWT by nudging the LSB of the quantised coefficient:
    quantised coefficient is even  →  bit 0
    quantised coefficient is odd   →  bit 1

Wire format is identical to the DCT/LSB modules:
    [4-byte big-endian length][encrypted data][4-byte 0xFFFFFFFF terminator]

Shape-stability guarantee
-------------------------
This module uses pywt mode='periodization', which gives:

    cA.shape == (ceil(h/2), ceil(w/2))   ← always exactly half, no overshoot
    idwt2(..., mode='periodization')     ← returns exactly (h, w), no padding

This eliminates ALL shape-mismatch errors regardless of whether the image
has odd or even dimensions.  No manual padding is needed.

Quantisation step
-----------------
Default is 64.  Haar LL coefficients are sums of 2×2 pixel blocks so a
±0.5 uint8 rounding error propagates as ±2 in the float coefficient domain.
With step=64, that error is only ±2/64 ≈ 0.03 — np.round will never
misclassify the LSB.  Do not go below 8 without testing on your images.

Lossless output only
--------------------
JPEG recompression will corrupt the payload.  The module raises ValueError
if a lossy output extension is requested.
"""

import struct
import warnings
from typing import Dict

import cv2
import numpy as np
import pywt  # pip install PyWavelets

from crypto import AESEncryption


_TERMINATOR         = 0xFFFFFFFF
_LOSSY_EXTS         = {"jpg", "jpeg"}
_DEFAULT_QUANT_STEP = 64
_WAVELET            = "haar"
_MODE               = "periodization"   # key: guarantees idwt2 returns exact (h, w)


# ---------------------------------------------------------------------------
# Bit-level helpers
# ---------------------------------------------------------------------------

def _to_bits(data: bytes) -> str:
    return "".join(format(b, "08b") for b in data)


def _bits_to_bytes(bits: str) -> bytes:
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class DWTSteganography:
    """Embed / extract secrets via single-level Haar DWT coefficient LSBs."""

    # ------------------------------------------------------------------
    # embed
    # ------------------------------------------------------------------
    @staticmethod
    def embed(
        image_path: str,
        secret: str,
        output_path: str,
        quantisation_step: int = _DEFAULT_QUANT_STEP,
    ) -> Dict:
        """
        Embed *secret* into *image_path* and write the result to *output_path*.

        Parameters
        ----------
        image_path        : Path to the carrier image (any OpenCV-readable format).
        secret            : Plaintext message to hide.
        output_path       : Destination — must be lossless (PNG / BMP / TIFF).
        quantisation_step : Robustness vs. visibility trade-off.
                            Must match the value used during extraction.
                            Default 64 is safe for standard uint8 PNG images.
        """
        # ---- Guard: refuse lossy output --------------------------------
        ext = output_path.rsplit(".", 1)[-1].lower()
        if ext in _LOSSY_EXTS:
            raise ValueError(
                f"DWT steganography requires a lossless output format. "
                f"'{ext}' is lossy and will destroy the payload. "
                "Use .png, .bmp, or .tiff instead."
            )

        if quantisation_step < 2:
            raise ValueError(
                f"quantisation_step must be >= 2; got {quantisation_step}."
            )

        # ---- Load as grayscale ----------------------------------------
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            bgr = cv2.imread(image_path)
            if bgr is None:
                raise ValueError(f"Cannot open image: {image_path}")
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # Store original dtype for later
        original_dtype = img.dtype
        h, w = img.shape

        # ---- Single-level Haar DWT with periodization -----------------
        # mode='periodization' guarantees:
        #   cA.shape == (ceil(h/2), ceil(w/2))
        #   idwt2 output == exactly (h, w)   ← no shape mismatch possible
        cA, (cH, cV, cD) = pywt.dwt2(
            img.astype(np.float64), _WAVELET, mode=_MODE
        )

        # Quantise LL sub-band
        cA_q = np.round(cA / quantisation_step).astype(np.int64)
        num_coeffs = cA_q.size

        # ---- Build payload --------------------------------------------
        encrypted   = AESEncryption.encrypt(secret)
        data_bytes  = encrypted.encode("utf-8")
        data_length = len(data_bytes)

        payload = (
            struct.pack(">I", data_length)
            + data_bytes
            + struct.pack(">I", _TERMINATOR)
        )
        bits       = _to_bits(payload)
        total_bits = len(bits)

        if total_bits > num_coeffs:
            raise ValueError(
                f"Message too large for DWT: needs {total_bits} coefficients, "
                f"LL sub-band only has {num_coeffs}. "
                "Use a larger image or a shorter message."
            )

        # ---- Embed bits via LSB flip of quantised coefficients ---------
        flat = cA_q.flatten()
        for i, bit in enumerate(bits):
            if bit == "1":
                flat[i] = flat[i] | np.int64(1)
            else:
                flat[i] = flat[i] & ~np.int64(1)

        # Important: Use exact multiplication and rounding
        cA_modified = (flat.reshape(cA_q.shape) * quantisation_step).astype(
            np.float64
        )

        # ---- Inverse DWT ----------------------------------------------
        # With mode='periodization' this is guaranteed to return (h, w).
        reconstructed = pywt.idwt2(
            (cA_modified, (cH, cV, cD)), _WAVELET, mode=_MODE
        )

        # Defensive check — should never fire with periodization
        rh, rw = reconstructed.shape
        if (rh, rw) != (h, w):
            raise RuntimeError(
                f"IDWT returned unexpected shape {reconstructed.shape} "
                f"(expected {img.shape}). "
                "This should not happen with mode='periodization'."
            )

        # Clip and convert back to original dtype
        result = np.clip(reconstructed, 0, 255).astype(original_dtype)
        
        # Save as PNG to preserve exact pixel values
        cv2.imwrite(output_path, result)

        return {
            "algorithm"         : "DWT",
            "wavelet"           : _WAVELET,
            "mode"              : _MODE,
            "quantisation_step" : quantisation_step,
            "bits_embedded"     : total_bits,
            "total_coefficients": num_coeffs,
            "encrypted_length"  : data_length,
            "image_size"        : f"{w}x{h}",
        }

    # ------------------------------------------------------------------
    # extract
    # ------------------------------------------------------------------
    @staticmethod
    def extract(
        image_path: str,
        quantisation_step: int = _DEFAULT_QUANT_STEP,
    ) -> str:
        """
        Recover and decrypt the secret previously embedded in *image_path*.

        *quantisation_step* MUST match the value used during embedding.
        """
        # Read image exactly as it was saved (grayscale)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            # Try reading as BGR and convert
            bgr = cv2.imread(image_path)
            if bgr is None:
                raise ValueError(f"Cannot open image: {image_path}")
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # Ensure float64 for consistent DWT computation
        img_float = img.astype(np.float64)

        # ---- Single-level Haar DWT with periodization -----------------
        # CRITICAL: We must decompose the image exactly as in embedding
        cA, (cH, cV, cD) = pywt.dwt2(img_float, _WAVELET, mode=_MODE)

        # Re-quantise using the same step as embedding
        cA_q = np.round(cA / quantisation_step).astype(np.int64)
        flat = cA_q.flatten()

        # ---- Extract raw bits from LSBs --------------------------------
        raw_bits = "".join(str(int(v) & 1) for v in flat)

        if len(raw_bits) < 32:
            raise ValueError("Not enough DWT coefficients for a length header.")

        # ---- Parse wire format ----------------------------------------
        # Extract length header (first 32 bits = 4 bytes)
        try:
            length_bytes = _bits_to_bytes(raw_bits[:32])
            data_length = struct.unpack(">I", length_bytes)[0]
        except Exception as exc:
            raise ValueError(f"Failed to parse length header: {exc}")

        # Validate data_length
        if data_length <= 0 or data_length > 10000000:  # Sanity check: 10MB max
            raise ValueError(
                f"DWT: Invalid data length {data_length}. "
                "Likely causes: wrong quantisation_step, or no data hidden."
            )

        # Calculate required bits for the data
        data_bits_needed = data_length * 8
        terminator_bits_needed = 32  # 4 bytes = 32 bits
        total_bits_needed = 32 + data_bits_needed + terminator_bits_needed

        if len(raw_bits) < total_bits_needed:
            raise ValueError(
                f"DWT: Not enough coefficients. Need {total_bits_needed} bits, "
                f"but only have {len(raw_bits)}. "
                "Likely causes: wrong quantisation_step or image was modified."
            )

        # Extract data bits
        data_start = 32
        data_end = data_start + data_bits_needed
        data_bits = raw_bits[data_start:data_end]
        data_bytes = _bits_to_bytes(data_bits)

        # Extract and verify terminator
        term_start = data_end
        term_end = term_start + 32
        term_bits = raw_bits[term_start:term_end]
        
        try:
            terminator = struct.unpack(">I", _bits_to_bytes(term_bits))[0]
        except Exception as exc:
            raise ValueError(f"Failed to parse terminator: {exc}")

        if terminator != _TERMINATOR:
            raise ValueError(
                f"DWT terminator mismatch (got 0x{terminator:08X}). "
                "Most likely causes:\n"
                f"  1. quantisation_step mismatch between embed and extract.\n"
                "  2. Image was re-saved through a lossy format (JPEG/WebP).\n"
                f"  3. quantisation_step too small — try a larger value "
                f"(current: {quantisation_step}, recommended default: "
                f"{_DEFAULT_QUANT_STEP}).\n"
                "  4. No hidden data in this image."
            )

        # ---- Decode and decrypt ---------------------------------------
        try:
            encrypted_str = data_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"DWT: UTF-8 decode failed: {exc}") from exc

        try:
            return AESEncryption.decrypt(encrypted_str)
        except Exception as exc:
            raise ValueError(f"DWT: AES decryption failed: {exc}") from exc

