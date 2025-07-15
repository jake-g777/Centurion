from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio

from src.database.database import get_db
from src.models.skin import Skin, Price, ArbitrageOpportunity
from src.services.price_monitor import PriceMonitor

router = APIRouter()

# Global price monitor instance (will be set by main.py)
price_monitor: Optional[PriceMonitor] = None

@router.get("/skins/{skin_name}")
async def get_skin_prices(
    skin_name: str,
    weapon: Optional[str] = Query(None, description="Weapon name (e.g., AK-47)"),
    db: Session = Depends(get_db)
):
    """Get current prices for a specific skin across all marketplaces"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        # Search for the skin
        prices = await price_monitor.search_skin_manual(skin_name, weapon)
        
        # Group prices by marketplace
        marketplace_prices = {}
        for price in prices:
            if price.marketplace not in marketplace_prices:
                marketplace_prices[price.marketplace] = []
            marketplace_prices[price.marketplace].append({
                "price": price.price,
                "currency": price.currency,
                "condition": price.condition,
                "stattrak": price.stattrak,
                "souvenir": price.souvenir,
                "url": price.url,
                "timestamp": price.timestamp.isoformat()
            })
        
        return {
            "skin_name": skin_name,
            "weapon": weapon,
            "prices": marketplace_prices,
            "total_marketplaces": len(marketplace_prices)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching skin: {str(e)}")

@router.get("/opportunities")
async def get_arbitrage_opportunities(
    min_profit: Optional[float] = Query(0.0, description="Minimum profit percentage"),
    max_profit: Optional[float] = Query(1000.0, description="Maximum profit percentage"),
    limit: Optional[int] = Query(50, description="Number of opportunities to return"),
    db: Session = Depends(get_db)
):
    """Get current arbitrage opportunities"""
    try:
        query = db.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.is_active == True,
            ArbitrageOpportunity.profit_percentage >= min_profit,
            ArbitrageOpportunity.profit_percentage <= max_profit
        ).order_by(ArbitrageOpportunity.net_profit.desc()).limit(limit)
        
        opportunities = query.all()
        
        # Get skin information for each opportunity
        result = []
        for opp in opportunities:
            skin = db.query(Skin).filter(Skin.id == opp.skin_id).first()
            opp_dict = opp.to_dict()
            opp_dict["skin_name"] = skin.name if skin else "Unknown"
            opp_dict["weapon"] = skin.weapon if skin else "Unknown"
            result.append(opp_dict)
        
        return {
            "opportunities": result,
            "total": len(result),
            "min_profit_filter": min_profit,
            "max_profit_filter": max_profit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting opportunities: {str(e)}")

@router.get("/opportunities/{skin_id}")
async def get_skin_opportunities(
    skin_id: int,
    db: Session = Depends(get_db)
):
    """Get arbitrage opportunities for a specific skin"""
    try:
        opportunities = db.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.skin_id == skin_id,
            ArbitrageOpportunity.is_active == True
        ).order_by(ArbitrageOpportunity.net_profit.desc()).all()
        
        skin = db.query(Skin).filter(Skin.id == skin_id).first()
        if not skin:
            raise HTTPException(status_code=404, detail="Skin not found")
        
        return {
            "skin": {
                "id": skin.id,
                "name": skin.name,
                "weapon": skin.weapon,
                "rarity": skin.rarity,
                "exterior": skin.exterior
            },
            "opportunities": [opp.to_dict() for opp in opportunities],
            "total_opportunities": len(opportunities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting skin opportunities: {str(e)}")

@router.get("/history/{skin_name}")
async def get_price_history(
    skin_name: str,
    days: Optional[int] = Query(7, description="Number of days of history to return"),
    db: Session = Depends(get_db)
):
    """Get price history for a skin"""
    try:
        from datetime import datetime, timedelta
        
        # Find the skin
        skin = db.query(Skin).filter(Skin.name == skin_name).first()
        if not skin:
            raise HTTPException(status_code=404, detail="Skin not found")
        
        # Get price history
        start_date = datetime.utcnow() - timedelta(days=days)
        prices = db.query(Price).filter(
            Price.skin_id == skin.id,
            Price.timestamp >= start_date
        ).order_by(Price.timestamp.asc()).all()
        
        # Group by marketplace and date
        history = {}
        for price in prices:
            marketplace = price.marketplace
            date_str = price.timestamp.strftime("%Y-%m-%d")
            
            if marketplace not in history:
                history[marketplace] = {}
            
            if date_str not in history[marketplace]:
                history[marketplace][date_str] = []
            
            history[marketplace][date_str].append({
                "price": price.price,
                "currency": price.currency,
                "timestamp": price.timestamp.isoformat(),
                "available": price.available,
                "listing_count": price.listing_count
            })
        
        return {
            "skin_name": skin_name,
            "weapon": skin.weapon,
            "history": history,
            "days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting price history: {str(e)}")

@router.get("/marketplaces")
async def get_marketplace_status():
    """Get status of all marketplaces"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        status = []
        for marketplace in price_monitor.marketplaces:
            is_available = await marketplace.is_available()
            status.append({
                "name": marketplace.name,
                "available": is_available,
                "base_url": marketplace.base_url
            })
        
        return {
            "marketplaces": status,
            "total_marketplaces": len(status),
            "available_marketplaces": len([m for m in status if m["available"]])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting marketplace status: {str(e)}")

@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics"""
    try:
        # Count skins
        total_skins = db.query(Skin).count()
        
        # Count recent prices
        from datetime import datetime, timedelta
        recent_time = datetime.utcnow() - timedelta(hours=1)
        recent_prices = db.query(Price).filter(Price.timestamp >= recent_time).count()
        
        # Count active opportunities
        active_opportunities = db.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.is_active == True
        ).count()
        
        # Get average profit percentage
        avg_profit = db.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.is_active == True
        ).with_entities(db.func.avg(ArbitrageOpportunity.profit_percentage)).scalar() or 0
        
        return {
            "total_skins": total_skins,
            "recent_prices": recent_prices,
            "active_opportunities": active_opportunities,
            "average_profit_percentage": round(avg_profit, 2),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.post("/search")
async def search_skins(
    query: str,
    weapon: Optional[str] = None,
    limit: Optional[int] = Query(20, description="Maximum number of results")
):
    """Search for skins across all marketplaces"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        prices = await price_monitor.search_skin_manual(query, weapon)
        
        # Group by skin name and get best prices
        skin_prices = {}
        for price in prices:
            # Create a key for the skin (name + condition + stattrak)
            skin_key = f"{price.condition}_{price.stattrak}_{price.souvenir}"
            
            if skin_key not in skin_prices:
                skin_prices[skin_key] = {
                    "condition": price.condition,
                    "stattrak": price.stattrak,
                    "souvenir": price.souvenir,
                    "marketplaces": {}
                }
            
            # Keep the lowest price for each marketplace
            if price.marketplace not in skin_prices[skin_key]["marketplaces"] or \
               price.price < skin_prices[skin_key]["marketplaces"][price.marketplace]["price"]:
                skin_prices[skin_key]["marketplaces"][price.marketplace] = {
                    "price": price.price,
                    "currency": price.currency,
                    "url": price.url
                }
        
        # Convert to list and sort by lowest price
        results = []
        for skin_key, data in skin_prices.items():
            if data["marketplaces"]:
                min_price = min(mp["price"] for mp in data["marketplaces"].values())
                results.append({
                    "condition": data["condition"],
                    "stattrak": data["stattrak"],
                    "souvenir": data["souvenir"],
                    "min_price": min_price,
                    "marketplaces": data["marketplaces"]
                })
        
        # Sort by minimum price and limit results
        results.sort(key=lambda x: x["min_price"])
        results = results[:limit]
        
        return {
            "query": query,
            "weapon": weapon,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching skins: {str(e)}") 