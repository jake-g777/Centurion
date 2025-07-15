import asyncio
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv

from src.services.marketplaces.csfloat import CSFloatMarketplace
from src.services.marketplaces.steam import SteamMarketplace
from src.services.marketplaces.base import SkinPrice

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplePriceMonitor:
    """Simplified price monitoring service without database"""
    
    def __init__(self):
        self.marketplaces = []
        self.is_running = False
        self.update_interval = int(os.getenv("UPDATE_INTERVAL", 300))  # 5 minutes default
        self.min_profit_threshold = float(os.getenv("MIN_PROFIT_THRESHOLD", 5.0))
        self.max_price_difference = float(os.getenv("MAX_PRICE_DIFFERENCE", 50.0))
        
        # Initialize marketplaces
        self._init_marketplaces()
    
    def _init_marketplaces(self):
        """Initialize all marketplace scrapers"""
        self.marketplaces = [
            CSFloatMarketplace(),
            SteamMarketplace(),
            # Add more marketplaces here as they're implemented
        ]
        logger.info(f"Initialized {len(self.marketplaces)} marketplaces")
    
    async def search_skin_manual(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Manually search for a skin across all marketplaces"""
        all_prices = []
        
        for marketplace in self.marketplaces:
            try:
                prices = await marketplace.search_skin(skin_name, weapon)
                all_prices.extend(prices)
                logger.info(f"Found {len(prices)} prices from {marketplace.name}")
            except Exception as e:
                logger.error(f"Error searching {marketplace} for {skin_name}: {e}")
        
        return all_prices
    
    async def find_arbitrage_opportunities(self, skin_name: str, weapon: str = None) -> List[Dict]:
        """Find arbitrage opportunities for a specific skin by matching exact item specifications"""
        prices = await self.search_skin_manual(skin_name, weapon)
        
        if len(prices) < 2:
            return []  # Need at least 2 marketplaces
        
        # Group prices by item specifications (weapon, skin, condition, stattrak, souvenir)
        item_groups = {}
        for price in prices:
            # Create a unique key for each item specification
            item_key = self._create_item_key(price, weapon, skin_name)
            
            if item_key not in item_groups:
                item_groups[item_key] = []
            item_groups[item_key].append(price)
        
        opportunities = []
        
        # For each item specification, find arbitrage opportunities
        for item_key, item_prices in item_groups.items():
            if len(item_prices) < 2:
                continue  # Need at least 2 marketplaces for this specific item
            
            # Group by marketplace and find lowest price per marketplace
            marketplace_prices = {}
            for price in item_prices:
                if price.marketplace not in marketplace_prices:
                    marketplace_prices[price.marketplace] = []
                marketplace_prices[price.marketplace].append(price)
            
            # Find lowest price per marketplace
            marketplace_lowest = {}
            for marketplace, price_list in marketplace_prices.items():
                marketplace_lowest[marketplace] = min(price_list, key=lambda p: p.price)
            
            # Find the lowest and highest prices across marketplaces
            if len(marketplace_lowest) < 2:
                continue
            
            lowest_price_obj = min(marketplace_lowest.values(), key=lambda p: p.price)
            highest_price_obj = max(marketplace_lowest.values(), key=lambda p: p.price)
            
            buy_price = lowest_price_obj.price
            sell_price = highest_price_obj.price
            buy_marketplace = lowest_price_obj.marketplace
            sell_marketplace = highest_price_obj.marketplace
            
            # Check if it's the same marketplace
            if buy_marketplace == sell_marketplace:
                continue
            
            # Check if price difference is significant
            if sell_price - buy_price < self.max_price_difference:
                continue
            
            # Calculate profit
            profit_amount = sell_price - buy_price
            profit_percentage = (profit_amount / buy_price) * 100
            
            # Check if profit meets threshold
            if profit_percentage < self.min_profit_threshold:
                continue
            
            # Calculate fees
            buy_fees = await self._get_marketplace_fees(buy_marketplace, buy_price)
            sell_fees = await self._get_marketplace_fees(sell_marketplace, sell_price)
            total_fees = buy_fees + sell_fees
            
            net_profit = profit_amount - total_fees
            
            # Only return opportunity if net profit is positive
            if net_profit <= 0:
                continue
            
            # Extract item details for the opportunity
            item_details = self._extract_item_details(lowest_price_obj, weapon, skin_name)
            
            opportunities.append({
                "skin_name": skin_name,
                "weapon": weapon,
                "condition": item_details["condition"],
                "stattrak": item_details["stattrak"],
                "souvenir": item_details["souvenir"],
                "buy_marketplace": buy_marketplace,
                "sell_marketplace": sell_marketplace,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "profit_amount": profit_amount,
                "profit_percentage": profit_percentage,
                "fees": total_fees,
                "net_profit": net_profit,
                "buy_url": lowest_price_obj.url,
                "sell_url": highest_price_obj.url,
                "detected_at": datetime.utcnow().isoformat()
            })
        
        # Sort by net profit (highest first)
        opportunities.sort(key=lambda x: x["net_profit"], reverse=True)
        
        return opportunities
    
    def _create_item_key(self, price, weapon: str, skin_name: str) -> str:
        """Create a unique key for item specifications"""
        # Normalize condition names
        condition = price.condition or ""
        condition = condition.lower().replace(" ", "_")
        
        # Create unique key
        key_parts = [
            weapon or "",
            skin_name or "",
            condition,
            "stattrak" if price.stattrak else "regular",
            "souvenir" if price.souvenir else "normal"
        ]
        
        return "|".join(key_parts)
    
    def _extract_item_details(self, price, weapon: str, skin_name: str) -> Dict:
        """Extract item details for display"""
        return {
            "weapon": weapon or "",
            "skin": skin_name or "",
            "condition": price.condition or "Unknown",
            "stattrak": price.stattrak,
            "souvenir": price.souvenir
        }
    
    async def _get_marketplace_fees(self, marketplace: str, price: float) -> float:
        """Get fees for a specific marketplace"""
        for mp in self.marketplaces:
            if mp.name.lower() in marketplace.lower():
                return await mp.get_fees(price)
        return 0.0
    
    async def get_marketplace_status(self) -> List[Dict]:
        """Get status of all marketplaces"""
        status = []
        for marketplace in self.marketplaces:
            try:
                is_available = await marketplace.is_available()
                status.append({
                    "name": marketplace.name,
                    "available": is_available,
                    "base_url": marketplace.base_url
                })
            except Exception as e:
                logger.error(f"Error checking {marketplace} status: {e}")
                status.append({
                    "name": marketplace.name,
                    "available": False,
                    "base_url": marketplace.base_url
                })
        
        return status
    
    async def get_popular_skins(self, limit: int = 20) -> List[Dict]:
        """Get list of popular skins to monitor"""
        all_skins = []
        
        for marketplace in self.marketplaces:
            try:
                skins = await marketplace.get_popular_skins(limit=limit//len(self.marketplaces))
                all_skins.extend(skins)
            except Exception as e:
                logger.error(f"Error getting popular skins from {marketplace}: {e}")
        
        # Remove duplicates and return unique skins
        unique_skins = []
        seen_names = set()
        
        for skin in all_skins:
            name = skin.get('name', '')
            if name and name not in seen_names:
                unique_skins.append(skin)
                seen_names.add(name)
        
        return unique_skins[:limit] 