"""
Ollama-backed AI chatbot with ethical safety filter.
"""
from typing import List

import requests

from config import Config
from ethics import EthicalFilter


class OllamaChatbot:
    """Thin wrapper around the Ollama HTTP API."""

    @staticmethod
    def is_running() -> bool:
        """Return ``True`` if the local Ollama service is reachable."""
        try:
            r = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    @staticmethod
    def available_models() -> List[str]:
        """Return the list of model names known to Ollama."""
        try:
            r = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if r.status_code == 200:
                return [m.get("name", "") for m in r.json().get("models", [])]
        except Exception:
            pass
        return []

    @staticmethod
    def chat(prompt: str, model: str = Config.OLLAMA_MODEL) -> str:
        """
        Send *prompt* to Ollama and return the assistant reply.

        Safety check is performed before the request; unsafe prompts are
        rejected with an explanation rather than forwarded to the LLM.
        """
        safe, reason = EthicalFilter.is_safe(prompt)
        if not safe:
            return f"I cannot respond to this query: {reason}"

        system_prompt = f"""{Config.ETHICAL_SYSTEM_PROMPT}

You are an expert steganography assistant. Provide accurate, helpful information about:
• Steganography techniques (LSB, DCT, DWT, Echo Hiding)
• Cryptography and encryption
• Digital security best practices
• Ethical uses of steganography

User question: {prompt}

Assistant response:"""

        payload = {
            "model"  : model,
            "prompt" : system_prompt,
            "stream" : False,
            "options": {"temperature": 0.7, "top_p": 0.9, "num_predict": 500},
        }

        try:
            r = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=60,
            )
            if r.status_code == 200:
                return r.json().get("response", "No response generated.")
            return f"Ollama returned HTTP {r.status_code}."
        except requests.Timeout:
            return "Ollama request timed out. The model may still be loading."
        except Exception as exc:
            return f"Error communicating with Ollama: {exc}"