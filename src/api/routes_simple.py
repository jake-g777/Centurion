from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict
import asyncio

from src.services.price_monitor_simple import SimplePriceMonitor
from src.data.weapon_skins import get_all_weapons, get_weapon_skins, get_weapons_by_category, get_all_categories, search_skins

router = APIRouter()

# Global price monitor instance (will be set by main.py)
price_monitor: Optional[SimplePriceMonitor] = None

@router.get("/skins/{skin_name}")
async def get_skin_prices(
    skin_name: str,
    weapon: Optional[str] = Query(None, description="Weapon name (e.g., AK-47)")
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
    skin_name: Optional[str] = Query(None, description="Specific skin to check"),
    weapon: Optional[str] = Query(None, description="Weapon name"),
    min_profit: Optional[float] = Query(0.0, description="Minimum profit percentage"),
    max_profit: Optional[float] = Query(1000.0, description="Maximum profit percentage")
):
    """Get arbitrage opportunities"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        if skin_name:
            # Check specific skin
            opportunities = await price_monitor.find_arbitrage_opportunities(skin_name, weapon)
        else:
            # Check popular skins
            popular_skins = await price_monitor.get_popular_skins(limit=10)
            opportunities = []
            
            for skin in popular_skins:
                skin_name = skin.get('name', '')
                if skin_name:
                    skin_opportunities = await price_monitor.find_arbitrage_opportunities(skin_name)
                    opportunities.extend(skin_opportunities)
        
        # Filter by profit percentage
        filtered_opportunities = [
            opp for opp in opportunities
            if min_profit <= opp["profit_percentage"] <= max_profit
        ]
        
        # Sort by net profit
        filtered_opportunities.sort(key=lambda x: x["net_profit"], reverse=True)
        
        return {
            "opportunities": filtered_opportunities,
            "total": len(filtered_opportunities),
            "min_profit_filter": min_profit,
            "max_profit_filter": max_profit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting opportunities: {str(e)}")

@router.get("/marketplaces")
async def get_marketplace_status():
    """Get status of all marketplaces"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        status = await price_monitor.get_marketplace_status()
        
        return {
            "marketplaces": status,
            "total_marketplaces": len(status),
            "available_marketplaces": len([m for m in status if m["available"]])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting marketplace status: {str(e)}")

@router.get("/stats")
async def get_statistics():
    """Get overall statistics"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        from datetime import datetime
        
        # Get marketplace status
        marketplace_status = await price_monitor.get_marketplace_status()
        available_marketplaces = len([m for m in marketplace_status if m["available"]])
        
        return {
            "total_marketplaces": len(marketplace_status),
            "available_marketplaces": available_marketplaces,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")

@router.post("/search")
async def search_skins(
    query: str = Body(..., embed=True),
    weapon: Optional[str] = Body(None, embed=True),
    limit: Optional[int] = Body(20, embed=True)
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

@router.get("/popular-skins")
async def get_popular_skins(
    limit: Optional[int] = Query(20, description="Number of skins to return")
):
    """Get list of popular skins"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        skins = await price_monitor.get_popular_skins(limit=limit)
        return {
            "skins": skins,
            "total": len(skins)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting popular skins: {str(e)}")

@router.get("/weapons")
async def get_weapons():
    """Get all available weapons"""
    try:
        weapons = get_all_weapons()
        return {
            "weapons": weapons,
            "total": len(weapons)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weapons: {str(e)}")

@router.get("/weapons/{weapon}/skins")
async def get_weapon_skins_endpoint(weapon: str):
    """Get all skins for a specific weapon"""
    try:
        skins = get_weapon_skins(weapon)
        return {
            "weapon": weapon,
            "skins": skins,
            "total": len(skins)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weapon skins: {str(e)}")

@router.get("/categories")
async def get_categories():
    """Get all weapon categories"""
    try:
        categories = get_all_categories()
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

@router.get("/categories/{category}/weapons")
async def get_weapons_by_category_endpoint(category: str):
    """Get weapons by category"""
    try:
        weapons = get_weapons_by_category(category)
        return {
            "category": category,
            "weapons": weapons,
            "total": len(weapons)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weapons by category: {str(e)}")

@router.get("/search-skins")
async def search_skins_endpoint(
    query: str = Query(..., description="Search query"),
    weapon: Optional[str] = Query(None, description="Filter by weapon")
):
    """Search for skins by name"""
    try:
        results = search_skins(query, weapon)
        return {
            "query": query,
            "weapon": weapon,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching skins: {str(e)}")

@router.post("/compare-prices")
async def compare_prices(
    weapon: str = Body(..., embed=True),
    skin: str = Body(..., embed=True)
):
    """Compare prices for a specific weapon skin across marketplaces"""
    if not price_monitor:
        raise HTTPException(status_code=503, detail="Price monitor not initialized")
    
    try:
        # Search for the skin
        prices = await price_monitor.search_skin_manual(skin, weapon)
        
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
        
        # Calculate arbitrage opportunities
        opportunities = await price_monitor.find_arbitrage_opportunities(skin, weapon)
        
        return {
            "weapon": weapon,
            "skin": skin,
            "prices": marketplace_prices,
            "total_marketplaces": len(marketplace_prices),
            "arbitrage_opportunities": opportunities,
            "lowest_price": min([p["price"] for prices_list in marketplace_prices.values() for p in prices_list]) if marketplace_prices else None,
            "highest_price": max([p["price"] for prices_list in marketplace_prices.values() for p in prices_list]) if marketplace_prices else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing prices: {str(e)}") 