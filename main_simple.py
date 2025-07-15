import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

from src.api.routes_simple import router as api_router
from src.web.routes_simple import router as web_router
from src.services.price_monitor_simple import SimplePriceMonitor

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="CS2 Arbitrage Tool (Simple)",
    description="Find arbitrage opportunities across CS2 skin marketplaces - No Database Version",
    version="1.0.0"
)

# Mount static files (only if directory exists)
import os
if os.path.exists("src/web/static"):
    app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(web_router)

# Global price monitor instance
price_monitor = None

@app.on_event("startup")
async def startup_event():
    """Initialize price monitoring on startup"""
    global price_monitor
    
    # Start price monitoring
    price_monitor = SimplePriceMonitor()
    
    # Set the global price monitor in the API routes
    from src.api.routes_simple import price_monitor as api_price_monitor
    import src.api.routes_simple
    src.api.routes_simple.price_monitor = price_monitor
    
    print("🚀 CS2 Arbitrage Tool started successfully!")
    print("📊 Web interface: http://localhost:8000")
    print("🔗 API documentation: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global price_monitor
    if price_monitor:
        price_monitor.is_running = False
        print("🛑 CS2 Arbitrage Tool stopped")

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 