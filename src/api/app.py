import sys
import os
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Add project root to sys.path to import src modules
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR / "src"))

from scout_core import core_engine

app = FastAPI(title="Vanguard Lens Dashboard")

# Setup templates
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serves the main dashboard UI."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/leads")
async def get_leads():
    """Returns all leads from the persistence layer."""
    try:
        leads = core_engine.persistence.query_entries()
        return leads
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats")
async def get_stats():
    """Returns basic stats about the ingested leads."""
    try:
        leads = core_engine.persistence.query_entries()
        stats = {
            "total_leads": len(leads),
            "providers": {}
        }
        for lead in leads:
            provider = lead.get("source_info", {}).get("scout", "unknown")
            stats["providers"][provider] = stats["providers"].get(provider, 0) + 1
        return stats
    except Exception as e:
        return {"error": str(e)}
