# StegoVault — Steganography System

AES-encrypted image steganography with LSB and DCT algorithms, served via a FastAPI backend and a dark-theme web UI.

## Project Structure

```
stego_project/
├── main.py               ← FastAPI app & all API routes
├── config.py             ← Central configuration (keys, model, safety keywords)
├── crypto.py             ← AES-CBC encrypt / decrypt helpers
├── ethics.py             ← Content-safety filter & ethical-guard injection
├── metrics.py            ← PSNR, SSIM, MSE, SNR quality metrics
├── chatbot.py            ← Ollama LLM integration
├── steganography/
│   ├── __init__.py
│   ├── system.py         ← Unified SteganographySystem facade
│   ├── lsb.py            ← LSB algorithm (embed / extract)
│   └── dct.py            ← DCT algorithm (embed / extract)
├── templates/
│   └── index.html        ← Dark-theme single-page UI
└── requirements.txt
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Start Ollama for the AI chatbot
ollama serve
ollama pull llama3.2

# 3. Run the server
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000** in your browser.

## API Endpoints

| Method | Path               | Description                         |
| ------ | ------------------ | ----------------------------------- |
| GET    | `/`                | Web UI                              |
| GET    | `/health`          | System status (Ollama, model)       |
| POST   | `/stego/embed`     | Embed encrypted secret in image     |
| POST   | `/stego/extract`   | Extract & decrypt secret from image |
| POST   | `/metrics/analyze` | PSNR / SSIM / MSE / SNR comparison  |
| POST   | `/chatbot/ask`     | Ask the AI assistant                |
| GET    | `/chatbot/models`  | List available Ollama models        |
| GET    | `/download/{file}` | Download a stego output file        |
| GET    | `/docs`            | Interactive Swagger UI              |

## Wire Format

Both LSB and DCT use the same payload layout inside the carrier:

```
┌──────────────┬─────────────────────┬─────────────────┐
│  4 B length  │  N B AES ciphertext  │  4 B 0xFFFFFFFF │
└──────────────┴─────────────────────┴─────────────────┘
```

- **length** — big-endian `uint32`, count of ciphertext bytes
- **ciphertext** — UTF-8 bytes of the Base64-encoded `IV || AES-CBC(secret)`
- **terminator** — `0xFFFFFFFF` integrity marker

## Ethical Safeguards

- Keyword blocklist rejects messages containing unsafe terms before embedding.
- An invisible ethical-guard header is prepended to every embedded payload; it is stripped automatically on extraction.
- The AI chatbot applies the same safety check before forwarding prompts to Ollama.
