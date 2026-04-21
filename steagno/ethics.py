"""
Ethical filtering: content-safety checks and hidden-prompt injection.
"""
import re
from datetime import datetime
from typing import Tuple

from config import Config


class EthicalFilter:
    """Detect unsafe content and annotate messages with an ethical guard."""

    # Patterns that suggest PII or other sensitive data
    _PII_PATTERNS = [
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",   # e-mail
        r"\b\d{3}[.\-]?\d{3}[.\-]?\d{4}\b",                           # phone
        r"\b\d{16}\b",                                                  # card number
    ]

    @staticmethod
    def is_safe(text: str) -> Tuple[bool, str]:
        """
        Return ``(True, "Content is safe")`` or ``(False, reason)``.
        """
        lower = text.lower()

        for kw in Config.UNSAFE_KEYWORDS:
            if kw in lower:
                return False, f"Contains unsafe keyword: '{kw}'"

        for pattern in EthicalFilter._PII_PATTERNS:
            if re.search(pattern, text):
                return False, "Contains sensitive personal information"

        if len(text.strip()) < 3:
            return False, "Content too short"

        return True, "Content is safe"

    @staticmethod
    def wrap_with_guard(text: str) -> str:
        """
        Prepend an ethical-guard timestamp block to *text*.
        This makes the guard invisible but recoverable on extraction.
        """
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"[ETHICAL_GUARD:{ts}]\n{Config.ETHICAL_SYSTEM_PROMPT}\n"
        return header + text

    @staticmethod
    def strip_guard(text: str) -> str:
        """Remove the ethical-guard header if present."""
        lines = text.splitlines()
        cleaned = [ln for ln in lines if not ln.startswith("[ETHICAL_GUARD:")]
        # Drop the system-prompt lines that follow the guard
        result_lines: list[str] = []
        skip = False
        for ln in lines:
            if ln.startswith("[ETHICAL_GUARD:"):
                skip = True
                continue
            if skip and ln.strip() == "":
                continue
            # Once we hit a non-empty line that isn't part of the prompt header, stop skipping
            if skip:
                prompt_lines = Config.ETHICAL_SYSTEM_PROMPT.splitlines()
                if ln in prompt_lines:
                    continue
                else:
                    skip = False
            result_lines.append(ln)
        return "\n".join(result_lines)