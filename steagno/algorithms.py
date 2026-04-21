"""
StegoVault — algorithm constants and routing identifiers.
"""

# Image algorithms — output must be lossless PNG
IMAGE_ALGORITHMS: set[str] = {"LSB", "DCT", "DWT"}

# Audio algorithms — output must be WAV
AUDIO_ALGORITHMS: set[str] = {"EchoHiding"}

# All recognised algorithm names
ALL_ALGORITHMS: set[str] = IMAGE_ALGORITHMS | AUDIO_ALGORITHMS

# Lossy image formats whose compression corrupts embedded data
LOSSY_IMAGE_EXTS: set[str] = {".jpg", ".jpeg", ".webp"}

# Lossy audio formats that destroy echo patterns
LOSSY_AUDIO_EXTS: set[str] = {".mp3", ".aac", ".ogg", ".m4a", ".wma"}

# Echo Hiding defaults (shared between embed & extract so values stay identical)
ECHO_D0              = 50
ECHO_D1              = 100
ECHO_DECAY           = 0.5
ECHO_SAMPLES_PER_BIT = 400


def normalise_algorithm(raw: str) -> str:
    """
    Case-insensitive algorithm name normalisation.
    Returns the canonical name or raises ValueError.
    """
    mapping = {a.lower(): a for a in ALL_ALGORITHMS}
    mapping["auto"] = "auto"
    key = raw.strip().lower()
    if key not in mapping:
        raise ValueError(
            f"Unknown algorithm '{raw}'. "
            f"Valid choices: {sorted(ALL_ALGORITHMS)} or 'auto'."
        )
    return mapping[key]


def is_audio_algorithm(algorithm: str) -> bool:
    return algorithm in AUDIO_ALGORITHMS