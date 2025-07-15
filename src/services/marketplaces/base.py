from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SkinPrice:
    """Data class for skin price information"""
    marketplace: str
    price: float
    currency: str = "USD"
    available: bool = True
    listing_count: int = 0
    timestamp: datetime = None
    url: str = ""
    condition: str = ""  # Factory New, Minimal Wear, etc.
    stattrak: bool = False
    souvenir: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class BaseMarketplace(ABC):
    """Base class for all marketplace scrapers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = self.__class__.__name__.replace("Marketplace", "")
        self.base_url = ""
        self.session = None
    
    @abstractmethod
    async def search_skin(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Search for a skin and return price information"""
        pass
    
    @abstractmethod
    async def get_skin_price(self, skin_id: str) -> Optional[SkinPrice]:
        """Get current price for a specific skin"""
        pass
    
    @abstractmethod
    async def get_popular_skins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of popular skins"""
        pass
    
    async def get_fees(self, price: float) -> float:
        """Calculate marketplace fees for a given price"""
        return 0.0
    
    async def is_available(self) -> bool:
        """Check if marketplace is available/accessible"""
        return True
    
    def __str__(self):
        return f"{self.name}Marketplace"
    
    def __repr__(self):
        return f"{self.name}Marketplace(api_key={'***' if self.api_key else None})" 