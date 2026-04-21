"""
Configuration settings for the Steganography System
"""
import hashlib
from Crypto.Cipher import AES


class Config:
   
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL    = "llama3.2:latest"

    # ── AES 
    SECRET_KEY = hashlib.sha256(b"steganography_master_key_2024").digest()[:32]
    AES_MODE   = AES.MODE_CBC
    IV_SIZE    = 16

    # ── Steganography
    MAX_CAPACITY_RATIO  = 0.5   # use at most 50 % of available LSB space
    COMPRESSION_QUALITY = 85    # JPEG quality when saving DCT output

    # ── Content Safety
    UNSAFE_KEYWORDS = [
        "cheat", "bypass", "hack", "jailbreak", "illegal",
        "exam", "test", "assignment", "plagiarism", "copyright",
        "terror", "exploit", "malware", "virus", "trojan",
    ]

    ETHICAL_SYSTEM_PROMPT = """You are a steganography assistant. You must NOT help with:
1. Academic cheating or plagiarism
2. Bypassing security systems
3. Illegal activities
4. Copyright infringement
5. Malicious software development

Always redirect such requests to ethical uses of steganography."""