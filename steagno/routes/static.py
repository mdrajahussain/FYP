"""
StegoVault — static UI route.
"""
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path(__file__).parent.parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))