import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("vanguard.api")

# Add project root to sys.path to import src modules
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR / "src"))

from scout_core import core_engine  # noqa: E402

app = FastAPI(title="Vanguard Lens Dashboard")

# Setup templates and static files
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health_check() -> JSONResponse:
    """Service health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "timestamp": time.time(), "version": "0.1.0-alpha.1"},
        status_code=status.HTTP_200_OK,
    )


@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request) -> Any:
    """Serves the main dashboard UI."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/leads")
async def get_leads() -> Any:
    """Returns all leads from the persistence layer."""
    try:
        leads = core_engine.leads.list_leads()
        return leads
    except Exception as e:
        logger.error(f"Failed to fetch leads: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/api/stats")
async def get_stats() -> Any:
    """Returns basic stats about the ingested leads using optimized DAO aggregates."""
    try:
        stats = core_engine.leads.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to fetch stats: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
