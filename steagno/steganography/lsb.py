"""
LSB (Least Significant Bit) Steganography for images.

Wire format embedded in the image LSBs
  ┌─────────────┬──────────────────────┬──────────────┐
  │  4 B length │  N B encrypted data  │  4 B 0xFF×4  │
  └─────────────┴──────────────────────┴──────────────┘
  • length  : big-endian uint32 = number of bytes in encrypted field
  • data    : UTF-8 bytes of the Base64-AES ciphertext
  • terminator : 0xFFFFFFFF (32 one-bits) for integrity check
"""
import struct
from typing import Dict

import numpy as np
from PIL import Image

from crypto import AESEncryption


_TERMINATOR = 0xFFFFFFFF


def _to_bits(data: bytes) -> str:
    return "".join(format(b, "08b") for b in data)


def _bits_to_bytes(bits: str) -> bytes:
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


class LSBSteganography:
    """Embed / extract secrets using the image's least-significant bits."""

    # ── embed ───────────────────────────────────────────────────────────────
    @staticmethod
    def embed(image_path: str, secret: str, output_path: str) -> Dict:
        """
        Encrypt *secret* and hide it in *image_path*; write to *output_path*.

        Returns a dict with capacity / usage statistics.
        """
        img       = Image.open(image_path).convert("RGB")
        arr       = np.array(img, dtype=np.uint8)
        h, w, ch  = arr.shape
        max_bits  = h * w * ch

        # Build payload
        encrypted   = AESEncryption.encrypt(secret)
        data_bytes  = encrypted.encode("utf-8")
        data_length = len(data_bytes)

        payload = (
            struct.pack(">I", data_length)
            + data_bytes
            + struct.pack(">I", _TERMINATOR)
        )
        bits = _to_bits(payload)

        if len(bits) > max_bits:
            raise ValueError(
                f"Message too large: needs {len(bits)} bits, "
                f"image capacity is {max_bits} bits."
            )

        # Embed bit-by-bit into LSBs
        flat = arr.flatten()
        for idx, bit in enumerate(bits):
            flat[idx] = (flat[idx] & 0xFE) | int(bit)

        result_arr = flat.reshape(arr.shape)
        Image.fromarray(result_arr).save(output_path)

        return {
            "algorithm"      : "LSB",
            "secret_length"  : len(secret),
            "encrypted_length": data_length,
            "total_bits"     : len(bits),
            "bits_used"      : len(bits),
            "capacity_used"  : f"{len(bits)}/{max_bits} ({100*len(bits)/max_bits:.2f}%)",
        }

    # ── extract ─────────────────────────────────────────────────────────────
    @staticmethod
    def extract(image_path: str) -> str:
        """
        Recover and decrypt the secret previously embedded in *image_path*.
        """
        img  = Image.open(image_path).convert("RGB")
        arr  = np.array(img, dtype=np.uint8)
        flat = arr.flatten()

        bits = "".join(str(v & 1) for v in flat)

        # --- length header (4 bytes = 32 bits) ---
        if len(bits) < 32:
            raise ValueError("Image too small to contain a length header.")

        data_length = struct.unpack(">I", _bits_to_bytes(bits[:32]))[0]

        max_possible = (len(bits) - 64) // 8
        if data_length <= 0 or data_length > max_possible:
            raise ValueError(
                f"Invalid embedded length: {data_length} "
                f"(max allowed: {max_possible})."
            )

        # --- data ---
        data_start = 32
        data_end   = data_start + data_length * 8
        if data_end > len(bits):
            raise ValueError("Not enough bits in image for the declared data length.")

        data_bytes = _bits_to_bytes(bits[data_start:data_end])

        # --- optional terminator check ---
        term_end = data_end + 32
        if term_end <= len(bits):
            term_val = struct.unpack(">I", _bits_to_bytes(bits[data_end:term_end]))[0]
            if term_val != _TERMINATOR:
                raise ValueError(
                    f"Terminator mismatch (got 0x{term_val:08X}); "
                    "data may be corrupted or no message was embedded."
                )

        # --- decode + decrypt ---
        try:
            encrypted_str = data_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Failed to decode extracted bytes as UTF-8: {exc}") from exc

        try:
            return AESEncryption.decrypt(encrypted_str)
        except Exception as exc:
            raise ValueError(f"AES decryption failed: {exc}") from exc