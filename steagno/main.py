
"""
StegoVault — entry point.

Run with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
or simply:
    python main.py

Algorithm matrix
----------------
┌─────────────┬────────┬────────────────────────────────────────────────────┐
│ Algorithm   │ Media  │ Notes                                              │
├─────────────┼────────┼────────────────────────────────────────────────────┤
│ LSB         │ Image  │ Output must stay PNG — JPEG destroys hidden bits.  │
│ DCT         │ Image  │ Output must stay PNG — JPEG re-quantises DCT coefs.│
│ DWT         │ Image  │ Output must stay PNG — same reason as DCT.         │
│ EchoHiding  │ Audio  │ Output must stay WAV — MP3/AAC destroys echoes.    │
└─────────────┴────────┴────────────────────────────────────────────────────┘

JPEG / WebP image inputs are auto-converted to PNG before embedding.
MP3 / AAC audio inputs are rejected at the extract step.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)