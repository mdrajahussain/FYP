
"""
SteganographySystem – unified facade over all algorithms.

Supported media types  →  algorithms
  image               →  LSB, DCT, DWT
  audio               →  EchoHiding
"""

import os
from typing import Dict

from ethics import EthicalFilter

from steganography.lsb         import LSBSteganography
from steganography.dct         import DCTSteganography
from steganography.dwt         import DWTSteganography
from steganography.echo_hiding import (
    EchoHidingSteganography,
    FIXED_D0, FIXED_D1, FIXED_DECAY, FIXED_SPB,
)


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
_AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aac"}

_IMAGE_ALGO_REGISTRY = [
    (LSBSteganography, "LSB"),
    (DCTSteganography, "DCT"),
    (DWTSteganography, "DWT"),
]

# Defaults aligned with echo_hiding.py FIXED_* constants
_ECHO_DEFAULTS = dict(
    d0=FIXED_D0,
    d1=FIXED_D1,
    decay=FIXED_DECAY,
    samples_per_bit=FIXED_SPB,
)


def _media_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _AUDIO_EXTS:
        return "audio"
    return "unknown"


def _echo_instance(**overrides) -> EchoHidingSteganography:
    """Return an EchoHidingSteganography instance, merging any parameter overrides."""
    params = {**_ECHO_DEFAULTS, **overrides}
    return EchoHidingSteganography(**params)


class SteganographySystem:
    """High-level embed / extract with ethical safety checks."""

    # ── Embed ───────────────────────────────────────────────────────────────

    @staticmethod
    def embed(
        media_path: str,
        secret: str,
        output_path: str,
        algorithm: str = "LSB",
        **algo_kwargs,
    ) -> Dict:
        """
        Embed *secret* into *media_path* using *algorithm*.

        Performs a content-safety check first and prepends the ethical guard.

        Parameters
        ----------
        media_path   Path to the carrier file.
        secret       Plaintext message to hide.
        output_path  Destination path for the stego file.
        algorithm    LSB / DCT / DWT (image) or EchoHiding (audio).
        **algo_kwargs
                     Forwarded to the algorithm, e.g. d0/d1/decay/
                     samples_per_bit for EchoHiding.
        """
        safe, reason = EthicalFilter.is_safe(secret)
        if not safe:
            raise ValueError(f"Unsafe content: {reason}")

        guarded = EthicalFilter.wrap_with_guard(secret)
        mtype   = _media_type(media_path)
        algo    = algorithm.strip().upper()

        # ── Image algorithms ─────────────────────────────────────────────
        if mtype == "image":
            if algo == "LSB":
                return LSBSteganography.embed(media_path, guarded, output_path, **algo_kwargs)
            if algo == "DCT":
                return DCTSteganography.embed(media_path, guarded, output_path, **algo_kwargs)
            if algo == "DWT":
                return DWTSteganography.embed(media_path, guarded, output_path, **algo_kwargs)
            raise ValueError(
                f"Unsupported image algorithm: '{algorithm}'. Valid: LSB, DCT, DWT."
            )

        # ── Audio algorithms ─────────────────────────────────────────────
        if mtype == "audio":
            if algo == "ECHOHIDING":
                return _echo_instance(**algo_kwargs).embed(media_path, guarded, output_path)
            raise ValueError(
                f"Unsupported audio algorithm: '{algorithm}'. Valid: EchoHiding."
            )

        raise ValueError(
            f"Unsupported media type for: '{media_path}'. "
            f"Supported — image: {sorted(_IMAGE_EXTS)}, audio: {sorted(_AUDIO_EXTS)}."
        )

    # ── Extract ─────────────────────────────────────────────────────────────

    @staticmethod
    def extract(
        media_path: str,
        algorithm: str = "auto",
        **algo_kwargs,
    ) -> str:
        """
        Extract the secret from *media_path*.

        Pass algorithm='auto' to try all algorithms for the detected media type.
        Returns the user message with the ethical-guard header stripped.
        """
        mtype = _media_type(media_path)
        if mtype == "unknown":
            raise ValueError(
                f"Cannot determine media type for: '{media_path}'. "
                f"Supported — image: {sorted(_IMAGE_EXTS)}, audio: {sorted(_AUDIO_EXTS)}."
            )

        raw = SteganographySystem._extract_raw(media_path, algorithm, mtype, **algo_kwargs)
        return EthicalFilter.strip_guard(raw)

    # ── Extract with explicit EchoHiding parameters ──────────────────────────

    @staticmethod
    def extract_with_params(
        media_path: str,
        algorithm: str,
        spb: int,
        d0: int,
        d1: int,
        decay: float = 0.5,
    ) -> str:
        """
        Extract using exact parameters — the most reliable method for EchoHiding.

        Parameters
        ----------
        media_path  Path to the stego audio file.
        algorithm   Must be "EchoHiding".
        spb         Samples per bit used at embed time.
        d0          Delay-0 used at embed time.
        d1          Delay-1 used at embed time.
        decay       Echo decay used at embed time.
        """
        algo = algorithm.strip().upper()
        if algo != "ECHOHIDING":
            raise ValueError(
                f"extract_with_params only supports EchoHiding; got '{algorithm}'."
            )

        mtype = _media_type(media_path)
        if mtype != "audio":
            raise ValueError(
                f"EchoHiding expects an audio file; got media type '{mtype}'."
            )

        echo_inst = EchoHidingSteganography(
            d0=d0, d1=d1, decay=decay, samples_per_bit=spb
        )
        raw = echo_inst.extract(media_path)
        return EthicalFilter.strip_guard(raw)

    # ── Internal ────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_raw(
        media_path: str,
        algorithm: str,
        mtype: str,
        **algo_kwargs,
    ) -> str:
        algo = algorithm.strip().upper()

        # Auto-detection
        if algo == "AUTO":
            if mtype == "image":
                candidates = _IMAGE_ALGO_REGISTRY
            elif mtype == "audio":
                # Try the fixed/default parameters first; they cover the most common case.
                candidates = [
                    (_echo_instance(), "EchoHiding(default)"),
                    (_echo_instance(samples_per_bit=500, d0=50, d1=120), "EchoHiding(500,50,120)"),
                    (_echo_instance(samples_per_bit=256, d0=20, d1=40), "EchoHiding(256,20,40)"),
                ]
            else:
                raise ValueError(f"Auto-detection not supported for media type: {mtype}")

            errors: list[str] = []
            for candidate, name in candidates:
                try:
                    if callable(getattr(candidate, "extract", None)):
                        result = candidate.extract(media_path)
                    else:
                        result = candidate.extract(media_path, **algo_kwargs)
                    return result
                except Exception as exc:
                    errors.append(f"{name}: {exc}")

            raise ValueError(
                "Could not extract data with any algorithm:\n" + "\n".join(errors)
            )

        # Explicit algorithm
        if algo == "LSB":
            if mtype != "image":
                raise ValueError("LSB is an image algorithm; got audio.")
            return LSBSteganography.extract(media_path, **algo_kwargs)

        if algo == "DCT":
            if mtype != "image":
                raise ValueError("DCT is an image algorithm; got audio.")
            return DCTSteganography.extract(media_path, **algo_kwargs)

        if algo == "DWT":
            if mtype != "image":
                raise ValueError("DWT is an image algorithm; got audio.")
            return DWTSteganography.extract(media_path, **algo_kwargs)

        if algo == "ECHOHIDING":
            if mtype != "audio":
                raise ValueError("EchoHiding is an audio algorithm; got image.")

            spb   = algo_kwargs.get("samples_per_bit")
            d0    = algo_kwargs.get("d0")
            d1    = algo_kwargs.get("d1")
            decay = algo_kwargs.get("decay", FIXED_DECAY)

            if spb and d0 and d1:
                echo_inst = EchoHidingSteganography(
                    d0=d0, d1=d1, decay=decay, samples_per_bit=spb
                )
            else:
                echo_inst = _echo_instance(**algo_kwargs)

            return echo_inst.extract(media_path)

        raise ValueError(
            f"Unknown algorithm: '{algorithm}'. Valid: LSB, DCT, DWT, EchoHiding, auto."
        )

    # ── Utilities ─────────────────────────────────────────────────────────

    @staticmethod
    def media_type(path: str) -> str:
        return _media_type(path)

    @staticmethod
    def supported_algorithms(media_path: str = "") -> Dict[str, list]:
        all_algos = {"image": ["LSB", "DCT", "DWT"], "audio": ["EchoHiding"]}
        if media_path:
            mtype = _media_type(media_path)
            return {mtype: all_algos.get(mtype, [])}
        return all_algos



