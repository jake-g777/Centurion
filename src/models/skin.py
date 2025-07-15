from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class Skin(Base):
    """Model representing a CS2 skin"""
    __tablename__ = "skins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    weapon = Column(String(100), nullable=False, index=True)
    rarity = Column(String(50), nullable=True)
    exterior = Column(String(50), nullable=True)  # Factory New, Minimal Wear, etc.
    pattern = Column(Integer, nullable=True)  # Pattern ID for special skins
    stattrak = Column(Boolean, default=False)
    souvenir = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Price(Base):
    """Model representing price data for a skin across marketplaces"""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    skin_id = Column(Integer, nullable=False, index=True)
    marketplace = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    available = Column(Boolean, default=True)
    listing_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert price record to dictionary"""
        return {
            "id": self.id,
            "skin_id": self.skin_id,
            "marketplace": self.marketplace,
            "price": self.price,
            "currency": self.currency,
            "available": self.available,
            "listing_count": self.listing_count,
            "timestamp": self.timestamp.isoformat()
        }

class ArbitrageOpportunity(Base):
    """Model representing detected arbitrage opportunities"""
    __tablename__ = "arbitrage_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    skin_id = Column(Integer, nullable=False, index=True)
    buy_marketplace = Column(String(100), nullable=False)
    sell_marketplace = Column(String(100), nullable=False)
    buy_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    profit_amount = Column(Float, nullable=False)
    profit_percentage = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    net_profit = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert arbitrage opportunity to dictionary"""
        return {
            "id": self.id,
            "skin_id": self.skin_id,
            "buy_marketplace": self.buy_marketplace,
            "sell_marketplace": self.sell_marketplace,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "profit_amount": self.profit_amount,
            "profit_percentage": self.profit_percentage,
            "fees": self.fees,
            "net_profit": self.net_profit,
            "detected_at": self.detected_at.isoformat(),
            "is_active": self.is_active
        } 