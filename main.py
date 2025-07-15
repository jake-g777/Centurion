import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

from src.api.routes import router as api_router
from src.web.routes import router as web_router
from src.services.price_monitor import PriceMonitor
from src.database.database import init_db

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CS2 Arbitrage Tool",
    description="Find arbitrage opportunities across CS2 skin marketplaces",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(web_router)

# Global price monitor instance
price_monitor = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and start price monitoring on startup"""
    global price_monitor
    
    # Initialize database
    await init_db()
    
    # Start price monitoring
    price_monitor = PriceMonitor()
    asyncio.create_task(price_monitor.start_monitoring())
    
    # Set the global price monitor in the API routes
    from src.api.routes import price_monitor as api_price_monitor
    import src.api.routes
    src.api.routes.price_monitor = price_monitor

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global price_monitor
    if price_monitor:
        await price_monitor.stop_monitoring()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 