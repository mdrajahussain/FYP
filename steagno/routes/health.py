"""
StegoVault — health-check route.
"""
from datetime import datetime

from fastapi import APIRouter

from algorithms import ALL_ALGORITHMS
from chatbot import OllamaChatbot
from config import Config

router = APIRouter()


@router.get("/health")
async def health():
    running = OllamaChatbot.is_running()
    return {
        "status"        : "healthy",
        "ollama_running": running,
        "model"         : Config.OLLAMA_MODEL if running else None,
        "timestamp"     : datetime.now().isoformat(),
        "algorithms"    : sorted(ALL_ALGORITHMS),
    }