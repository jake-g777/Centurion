from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Search page"""
    return templates.TemplateResponse("search.html", {"request": request})

@router.get("/opportunities", response_class=HTMLResponse)
async def opportunities_page(request: Request):
    """Opportunities page"""
    return templates.TemplateResponse("opportunities.html", {"request": request})

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Price history page"""
    return templates.TemplateResponse("history.html", {"request": request})

@router.get("/api/opportunities-data")
async def get_opportunities_data(
    min_profit: Optional[float] = Query(0.0),
    max_profit: Optional[float] = Query(1000.0),
    limit: Optional[int] = Query(50)
):
    """Get opportunities data for the web interface"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/opportunities",
            params={
                "min_profit": min_profit,
                "max_profit": max_profit,
                "limit": limit
            }
        )
        return response.json()

@router.get("/api/stats-data")
async def get_stats_data():
    """Get statistics data for the web interface"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/stats")
        return response.json()

@router.get("/api/marketplace-status")
async def get_marketplace_status():
    """Get marketplace status for the web interface"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/marketplaces")
        return response.json() 