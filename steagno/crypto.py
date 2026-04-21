"""
AES-CBC encryption / decryption helpers
"""
import os
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from config import Config


class AESEncryption:
    """Symmetric AES-CBC encryption with random IV."""

    @staticmethod
    def encrypt(plaintext: str, key: bytes = Config.SECRET_KEY) -> str:
        """
        Encrypt *plaintext* and return a Base64 string.
        Format: base64( IV || ciphertext )
        """
        iv      = os.urandom(Config.IV_SIZE)
        cipher  = AES.new(key, Config.AES_MODE, iv)
        ct      = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
        return base64.b64encode(iv + ct).decode("utf-8")

    @staticmethod
    def decrypt(b64_data: str, key: bytes = Config.SECRET_KEY) -> str:
        """
        Decrypt a Base64 string produced by :meth:`encrypt`.
        """
        raw       = base64.b64decode(b64_data)
        iv        = raw[:Config.IV_SIZE]
        ciphertext = raw[Config.IV_SIZE:]
        cipher    = AES.new(key, Config.AES_MODE, iv)
        return unpad(cipher.decrypt(ciphertext), AES.block_size).decode("utf-8")