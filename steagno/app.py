"""
AI-Powered Multimedia Steganography System — FastAPI application factory.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import health, steganography, metrics, chatbot, static, auth, echo, video

from core.db import Base, engine
from models.user import User


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-Powered Multimedia Steganography System",
        description=(
            "AES-encrypted steganography supporting LSB, DCT, DWT (image) "
            "and Echo Hiding (audio) algorithms."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(static.router)
    app.include_router(health.router)
    app.include_router(auth.router, prefix="")
    app.include_router(steganography.router, prefix="/stego")
    app.include_router(metrics.router, prefix="/metrics")
    app.include_router(chatbot.router, prefix="/chatbot")

    #echo hiding for audio
    app.include_router(echo.router)
    app.include_router(video.router)

    app.add_event_handler("startup", startup_handler)

    return app




async def startup_handler():
    import time
    from pathlib import Path
    from chatbot import OllamaChatbot
    from storage import UPLOADS_DIR, OUTPUTS_DIR

    Base.metadata.create_all(bind=engine)

    cutoff = time.time() - 86_400
    for d in (UPLOADS_DIR, OUTPUTS_DIR):
        for f in d.iterdir():
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
            except Exception:
                pass

    print("\n" + "=" * 60)
    print("  StegoVault v3.0 — Steganography System")
    print("=" * 60)
    print("  UI  : http://0.0.0.0:8000")
    print("  Docs: http://127.0.0.1:8000/docs")



    if OllamaChatbot.is_running():
        models = OllamaChatbot.available_models()
        print(f"\n   Ollama running | models: {', '.join(models) or 'none'}")
    else:
        print("\n   Ollama not running (chatbot disabled)")
        print("     https://ollama.com/  then: ollama serve")

    print("\n  Image algorithms : LSB · DCT  (output: PNG)")
    print("  Audio algorithms : EchoHiding        (output: WAV)")
    print("  Video algorithms : DWT                (output: MP4)")
    print("=" * 60 + "\n")