"""
DCT (Discrete Cosine Transform) Steganography for images.

One bit is stored per 8×8 block by forcing the sign of the (5,5)
frequency coefficient:
    positive  →  bit 1
    negative  →  bit 0

Wire format is identical to the LSB module:
    [4-byte big-endian length][encrypted data][4-byte 0xFFFFFFFF terminator]
"""
import struct
from typing import Dict

import cv2
import numpy as np

from config import Config
from crypto import AESEncryption


_TERMINATOR = 0xFFFFFFFF


def _to_bits(data: bytes) -> str:
    return "".join(format(b, "08b") for b in data)


def _bits_to_bytes(bits: str) -> bytes:
    return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))


class DCTSteganography:
    """Embed / extract secrets via DCT coefficient manipulation."""

    @staticmethod
    def embed(
        image_path: str,
        secret: str,
        output_path: str,
        strength: float = 50.0,
    ) -> Dict:
        """
        Embed *secret* in *image_path* using DCT; write to *output_path*.

        *strength* controls how aggressively the (5,5) coefficient is pushed —
        larger values are more robust but slightly more visible.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            # Try converting via colour read
            bgr = cv2.imread(image_path)
            if bgr is None:
                raise ValueError(f"Cannot open image: {image_path}")
            img = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        h, w = img.shape
        num_blocks = (h // 8) * (w // 8)

        # Build payload
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

        if total_bits > num_blocks:
            raise ValueError(
                f"Message too large for DCT: needs {total_bits} blocks, "
                f"image only has {num_blocks}."
                f"Solutions: use a smaller message, reduce AES key size, or choose a larger image (width , height)."
            )

        work = img.astype(np.float64)
        bit_idx = 0

        for y in range(0, h - 7, 8):
            for x in range(0, w - 7, 8):
                if bit_idx >= total_bits:
                    break
                block   = work[y : y + 8, x : x + 8]
                dct_blk = cv2.dct(block.astype(np.float32))

                magnitude = max(abs(float(dct_blk[5, 5])), strength)
                if bits[bit_idx] == "1":
                    dct_blk[5, 5] = magnitude
                else:
                    dct_blk[5, 5] = -magnitude

                work[y : y + 8, x : x + 8] = cv2.idct(dct_blk)
                bit_idx += 1
            if bit_idx >= total_bits:
                break

        result = np.clip(work, 0, 255).astype(np.uint8)
        # Prefer lossless; fall back to JPEG with high quality
        ext = output_path.rsplit(".", 1)[-1].lower()
        if ext in ("jpg", "jpeg"):
            cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, Config.COMPRESSION_QUALITY])
        else:
            cv2.imwrite(output_path, result)

        return {
            "algorithm"      : "DCT",
            "strength"       : strength,
            "bits_embedded"  : bit_idx,
            "total_bits"     : total_bits,
            "encrypted_length": data_length,
        }

    @staticmethod
    def extract(image_path: str) -> str:
        """
        Recover and decrypt the secret previously embedded in *image_path*.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Cannot open image: {image_path}")

        h, w = img.shape
        raw_bits: list[str] = []

        for y in range(0, h - 7, 8):
            for x in range(0, w - 7, 8):
                block   = img[y : y + 8, x : x + 8].astype(np.float32)
                dct_blk = cv2.dct(block)
                raw_bits.append("1" if dct_blk[5, 5] > 0 else "0")

        bit_string = "".join(raw_bits)

        if len(bit_string) < 32:
            raise ValueError("Not enough DCT blocks for a length header.")

        data_length = struct.unpack(">I", _bits_to_bytes(bit_string[:32]))[0]
        max_possible = (len(bit_string) - 64) // 8
        if data_length <= 0 or data_length > max_possible:
            raise ValueError(
                f"DCT: invalid data length {data_length} "
                f"(max allowed: {max_possible})."
            )

        data_start = 32
        data_end   = data_start + data_length * 8
        if data_end > len(bit_string):
            raise ValueError("DCT: not enough bits for the declared data length.")

        data_bytes = _bits_to_bytes(bit_string[data_start:data_end])

        # Optional terminator check
        term_end = data_end + 32
        if term_end <= len(bit_string):
            term_val = struct.unpack(">I", _bits_to_bytes(bit_string[data_end:term_end]))[0]
            if term_val != _TERMINATOR:
                raise ValueError(
                    f"DCT terminator mismatch (got 0x{term_val:08X}); "
                    "data may be corrupted."
                )

        try:
            encrypted_str = data_bytes.decode("utf-8", errors="replace")
        except Exception:
            raise ValueError(
                "DCT: Extraction failed. The embedded data is severely corrupted. "
                "Ensure the image wasn't heavily compressed or resized."
            )

        try:
            return AESEncryption.decrypt(encrypted_str)
        except Exception as exc:
            raise ValueError(
                "DCT: AES decryption failed. This usually means the image was "
                "compressed (e.g., JPEG) and the payload bits were lost or corrupted."
            ) from exc