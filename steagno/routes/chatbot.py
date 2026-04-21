"""
StegoVault — chatbot routes.

Mounted at /chatbot by the app factory.
"""
from datetime import datetime

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from chatbot import OllamaChatbot
from config import Config

router = APIRouter()


@router.post("/ask")
async def ask_chatbot(
    query: str = Form(...),
    model: str = Form(Config.OLLAMA_MODEL),
):
    if not OllamaChatbot.is_running():
        return JSONResponse({
            "success": False,
            "message": "Ollama is not running. Start it with: ollama serve",
        })

    try:
        reply = OllamaChatbot.chat(query, model)
        return {
            "success"  : True,
            "query"    : query,
            "response" : reply,
            "model"    : model,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        return JSONResponse({"success": False, "message": str(exc)})


@router.get("/models")
async def chatbot_models():
    return {
        "success": True,
        "models" : OllamaChatbot.available_models(),
        "default": Config.OLLAMA_MODEL,
    }