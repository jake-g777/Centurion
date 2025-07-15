import asyncio
import os
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

from src.services.marketplaces.csfloat import CSFloatMarketplace
from src.services.marketplaces.steam import SteamMarketplace
from src.services.marketplaces.base import SkinPrice
from src.database.database import SessionLocal
from src.models.skin import Skin, Price, ArbitrageOpportunity

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceMonitor:
    """Main price monitoring service"""
    
    def __init__(self):
        self.marketplaces = []
        self.monitoring_task = None
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
    
    async def start_monitoring(self):
        """Start the price monitoring loop"""
        if self.is_running:
            logger.warning("Price monitoring is already running")
            return
        
        self.is_running = True
        logger.info("Starting price monitoring...")
        
        while self.is_running:
            try:
                await self._monitor_prices()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in price monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_monitoring(self):
        """Stop the price monitoring loop"""
        self.is_running = False
        logger.info("Stopping price monitoring...")
    
    async def _monitor_prices(self):
        """Monitor prices across all marketplaces"""
        logger.info("Starting price update cycle...")
        
        # Get popular skins to monitor
        popular_skins = await self._get_popular_skins()
        
        for skin_info in popular_skins:
            try:
                await self._update_skin_prices(skin_info)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error updating prices for {skin_info.get('name', 'unknown')}: {e}")
        
        # Detect arbitrage opportunities
        await self._detect_arbitrage_opportunities()
        
        logger.info("Price update cycle completed")
    
    async def _get_popular_skins(self) -> List[Dict]:
        """Get list of popular skins to monitor"""
        all_skins = []
        
        for marketplace in self.marketplaces:
            try:
                skins = await marketplace.get_popular_skins(limit=50)
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
        
        return unique_skins[:100]  # Limit to top 100
    
    async def _update_skin_prices(self, skin_info: Dict):
        """Update prices for a specific skin across all marketplaces"""
        skin_name = skin_info.get('name', '')
        weapon = skin_info.get('weapon', '')
        
        if not skin_name:
            return
        
        # Get or create skin record
        db = SessionLocal()
        try:
            skin = db.query(Skin).filter(Skin.name == skin_name).first()
            if not skin:
                skin = Skin(
                    name=skin_name,
                    weapon=weapon,
                    rarity=skin_info.get('rarity', ''),
                    exterior=skin_info.get('exterior', ''),
                    stattrak=skin_info.get('stattrak', False),
                    souvenir=skin_info.get('souvenir', False)
                )
                db.add(skin)
                db.commit()
                db.refresh(skin)
            
            # Get prices from all marketplaces
            for marketplace in self.marketplaces:
                try:
                    prices = await marketplace.search_skin(skin_name, weapon)
                    
                    for price_data in prices:
                        # Save price to database
                        price_record = Price(
                            skin_id=skin.id,
                            marketplace=price_data.marketplace,
                            price=price_data.price,
                            currency=price_data.currency,
                            available=price_data.available,
                            listing_count=price_data.listing_count
                        )
                        db.add(price_record)
                    
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error getting prices from {marketplace} for {skin_name}: {e}")
                    
        finally:
            db.close()
    
    async def _detect_arbitrage_opportunities(self):
        """Detect arbitrage opportunities from current prices"""
        db = SessionLocal()
        try:
            # Get recent prices (last 10 minutes)
            recent_time = datetime.utcnow() - timedelta(minutes=10)
            
            # Get all skins with recent prices
            skins_with_prices = db.query(Skin).join(Price).filter(
                Price.timestamp >= recent_time
            ).distinct().all()
            
            for skin in skins_with_prices:
                await self._analyze_skin_arbitrage(skin, db)
                
        finally:
            db.close()
    
    async def _analyze_skin_arbitrage(self, skin: Skin, db):
        """Analyze arbitrage opportunities for a specific skin"""
        # Get recent prices for this skin
        recent_time = datetime.utcnow() - timedelta(minutes=10)
        prices = db.query(Price).filter(
            Price.skin_id == skin.id,
            Price.timestamp >= recent_time,
            Price.available == True
        ).all()
        
        if len(prices) < 2:
            return  # Need at least 2 marketplaces
        
        # Group prices by marketplace
        marketplace_prices = {}
        for price in prices:
            if price.marketplace not in marketplace_prices:
                marketplace_prices[price.marketplace] = []
            marketplace_prices[price.marketplace].append(price.price)
        
        # Find lowest and highest prices
        all_prices = [price.price for price in prices]
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        # Check if price difference is significant
        if max_price - min_price < self.max_price_difference:
            return
        
        # Find marketplaces with min and max prices
        buy_marketplace = None
        sell_marketplace = None
        
        for marketplace, price_list in marketplace_prices.items():
            if min(price_list) == min_price:
                buy_marketplace = marketplace
            if max(price_list) == max_price:
                sell_marketplace = marketplace
        
        if not buy_marketplace or not sell_marketplace or buy_marketplace == sell_marketplace:
            return
        
        # Calculate profit
        profit_amount = max_price - min_price
        profit_percentage = (profit_amount / min_price) * 100
        
        # Check if profit meets threshold
        if profit_percentage < self.min_profit_threshold:
            return
        
        # Calculate fees
        buy_fees = await self._get_marketplace_fees(buy_marketplace, min_price)
        sell_fees = await self._get_marketplace_fees(sell_marketplace, max_price)
        total_fees = buy_fees + sell_fees
        
        net_profit = profit_amount - total_fees
        
        # Only create opportunity if net profit is positive
        if net_profit <= 0:
            return
        
        # Check if this opportunity already exists
        existing = db.query(ArbitrageOpportunity).filter(
            ArbitrageOpportunity.skin_id == skin.id,
            ArbitrageOpportunity.buy_marketplace == buy_marketplace,
            ArbitrageOpportunity.sell_marketplace == sell_marketplace,
            ArbitrageOpportunity.is_active == True
        ).first()
        
        if existing:
            # Update existing opportunity
            existing.buy_price = min_price
            existing.sell_price = max_price
            existing.profit_amount = profit_amount
            existing.profit_percentage = profit_percentage
            existing.fees = total_fees
            existing.net_profit = net_profit
            existing.detected_at = datetime.utcnow()
        else:
            # Create new opportunity
            opportunity = ArbitrageOpportunity(
                skin_id=skin.id,
                buy_marketplace=buy_marketplace,
                sell_marketplace=sell_marketplace,
                buy_price=min_price,
                sell_price=max_price,
                profit_amount=profit_amount,
                profit_percentage=profit_percentage,
                fees=total_fees,
                net_profit=net_profit
            )
            db.add(opportunity)
        
        db.commit()
        logger.info(f"Arbitrage opportunity detected for {skin.name}: {buy_marketplace} -> {sell_marketplace}, Profit: ${net_profit:.2f} ({profit_percentage:.1f}%)")
    
    async def _get_marketplace_fees(self, marketplace: str, price: float) -> float:
        """Get fees for a specific marketplace"""
        for mp in self.marketplaces:
            if mp.name.lower() in marketplace.lower():
                return await mp.get_fees(price)
        return 0.0
    
    async def search_skin_manual(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Manually search for a skin across all marketplaces"""
        all_prices = []
        
        for marketplace in self.marketplaces:
            try:
                prices = await marketplace.search_skin(skin_name, weapon)
                all_prices.extend(prices)
            except Exception as e:
                logger.error(f"Error searching {marketplace} for {skin_name}: {e}")
        
        return all_prices
    
    async def get_current_opportunities(self) -> List[Dict]:
        """Get current arbitrage opportunities"""
        db = SessionLocal()
        try:
            opportunities = db.query(ArbitrageOpportunity).filter(
                ArbitrageOpportunity.is_active == True
            ).order_by(ArbitrageOpportunity.net_profit.desc()).limit(50).all()
            
            return [opp.to_dict() for opp in opportunities]
        finally:
            db.close() 