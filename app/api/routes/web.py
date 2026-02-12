"""
Web UI Routes
Serves the Bootstrap dashboard interface
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Setup templates - navigate from routes -> api -> app -> templates
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(tags=["Web UI"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Main dashboard interface
    
    Provides Bootstrap UI for:
    - Address input
    - 66-point analysis
    - Interactive results display
    - XAI explanations
    - Performance metrics
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api-sources", response_class=HTMLResponse)
async def api_sources(request: Request):
    """
    Data Sources documentation page
    
    Shows all API data sources used for analysis
    """
    return templates.TemplateResponse("api_sources.html", {"request": request})

