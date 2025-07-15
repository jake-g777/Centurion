import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
import json
import re
from datetime import datetime
import os
from bs4 import BeautifulSoup

from .base import BaseMarketplace, SkinPrice

class SteamMarketplace(BaseMarketplace):
    """Steam Marketplace scraper"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("STEAM_API_KEY"))
        self.base_url = "https://steamcommunity.com"
        self.market_url = "https://steamcommunity.com/market"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    
    async def search_skin(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Search for a skin on Steam Marketplace"""
        try:
            # Build search query
            query = skin_name
            if weapon:
                query = f"{weapon} {skin_name}"
            
            # Try Steam Web API first if we have an API key
            if self.api_key:
                try:
                    return await self._search_steam_api(query)
                except Exception as e:
                    print(f"Steam API search failed: {e}, falling back to market scraping")
            
            # Fallback to Steam market search URL
            search_url = f"{self.market_url}/search/render"
            params = {
                "appid": 730,  # CS2 app ID
                "norender": 1,
                "count": 50,
                "search_descriptions": 0,
                "sort_column": "price",
                "sort_dir": "asc",
                "query": query
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._parse_steam_listings(data.get("results", []))
                    else:
                        print(f"Steam search failed: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Error searching Steam: {e}")
            return []
    
    async def _search_steam_api(self, query: str) -> List[SkinPrice]:
        """Search using Steam Internal Web API"""
        try:
            # Steam Internal Web API endpoints (from https://github.com/Revadike/InternalSteamWebAPI/wiki)
            api_base = "https://steamcommunity.com"
            
            # Try different Steam internal API endpoints for market data
            endpoints_to_try = [
                f"{api_base}/market/search/render?appid=730&norender=1&count=50&search_descriptions=0&sort_column=price&sort_dir=asc&query={query}",
                f"{api_base}/market/popular?appid=730&query={query}",
                f"{api_base}/market/priceoverview?appid=730&currency=1&market_hash_name={query}"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    # Use more realistic browser headers for internal API
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "Referer": "https://steamcommunity.com/market/",
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, headers=headers) as response:
                            print(f"Trying Steam Internal API endpoint: {endpoint} - Status: {response.status}")
                            
                            if response.status == 200:
                                data = await response.json()
                                print(f"Steam Internal API response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                                
                                # Parse the response based on the endpoint
                                if "search/render" in endpoint:
                                    return await self._parse_steam_listings(data.get("results", []))
                                elif "popular" in endpoint:
                                    return self._parse_steam_popular(data)
                                elif "priceoverview" in endpoint:
                                    return self._parse_steam_price_overview(data, query)
                                else:
                                    return self._parse_steam_api_generic(data)
                            elif response.status == 429:
                                print("Steam rate limited (429) - too many requests")
                                continue
                            elif response.status == 403:
                                print("Steam forbidden (403) - access denied")
                                continue
                            else:
                                print(f"Steam Internal API endpoint failed: {response.status}")
                                continue
                                
                except Exception as e:
                    print(f"Error with Steam Internal API endpoint {endpoint}: {e}")
                    continue
            
            print("All Steam Internal API endpoints failed, no data returned")
            return []
            
        except Exception as e:
            print(f"Error in Steam Internal API search: {e}")
            return []
    
    def _parse_steam_popular(self, data: Dict) -> List[SkinPrice]:
        """Parse Steam popular items response"""
        prices = []
        try:
            # Parse popular items data
            items = data.get("items", [])
            for item in items:
                try:
                    price = self._parse_steam_listing(item)
                    if price:
                        prices.append(price)
                except Exception as e:
                    continue
            return prices
        except Exception as e:
            print(f"Error parsing Steam popular items: {e}")
            return prices
    
    def _parse_steam_price_overview(self, data: Dict, query: str) -> List[SkinPrice]:
        """Parse Steam price overview response"""
        prices = []
        try:
            # Price overview gives current market price
            if data.get("success") and data.get("lowest_price"):
                price_text = data.get("lowest_price", "")
                price = float(re.sub(r'[^\d.]', '', price_text))
                
                prices.append(SkinPrice(
                    marketplace="Steam",
                    price=price,
                    currency="USD",
                    available=True,
                    listing_count=1,
                    timestamp=datetime.utcnow(),
                    url=f"https://steamcommunity.com/market/listings/730/{query}",
                    condition="",
                    stattrak=False,
                    souvenir=False
                ))
            return prices
        except Exception as e:
            print(f"Error parsing Steam price overview: {e}")
            return prices
    
    def _parse_steam_api_generic(self, data: Dict) -> List[SkinPrice]:
        """Parse generic Steam API response"""
        prices = []
        try:
            # Try to extract any price data from generic response
            print(f"Generic Steam API response: {data}")
            return prices
        except Exception as e:
            print(f"Error parsing Steam API generic: {e}")
            return prices
    
    async def get_skin_price(self, skin_id: str) -> Optional[SkinPrice]:
        """Get current price for a specific skin"""
        try:
            # Steam market item URL
            url = f"{self.market_url}/listings/730/{skin_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_steam_page(html, skin_id)
                    else:
                        return None
                        
        except Exception as e:
            print(f"Error getting Steam price: {e}")
            return None
    
    async def get_popular_skins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of popular skins from Steam"""
        try:
            url = f"{self.market_url}/search/render"
            params = {
                "appid": 730,
                "norender": 1,
                "count": limit,
                "sort_column": "volume",
                "sort_dir": "desc"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        return []
                        
        except Exception as e:
            print(f"Error getting popular skins from Steam: {e}")
            return []
    
    async def _parse_steam_listings(self, listings: List[Dict]) -> List[SkinPrice]:
        """Parse Steam listings into SkinPrice objects"""
        prices = []
        
        for listing in listings:
            try:
                price = self._parse_steam_listing(listing)
                if price:
                    prices.append(price)
            except Exception as e:
                print(f"Error parsing Steam listing: {e}")
                continue
        
        return prices
    
    def _parse_steam_listing(self, listing: Dict) -> Optional[SkinPrice]:
        """Parse a single Steam listing"""
        try:
            # Extract price
            price_text = listing.get("sell_price_text", "")
            if not price_text:
                return None
            
            # Convert price to float (remove currency symbol and commas)
            price = float(re.sub(r'[^\d.]', '', price_text))
            
            # Extract item info
            name = listing.get("name", "")
            listing_id = listing.get("listingid", "")
            
            # Build URL
            url = f"{self.market_url}/listings/730/{listing_id}" if listing_id else ""
            
            # Extract condition from name
            condition = self._extract_condition(name)
            stattrak = "StatTrak" in name
            souvenir = "Souvenir" in name
            
            return SkinPrice(
                marketplace="Steam",
                price=price,
                currency="USD",
                available=True,
                listing_count=1,
                timestamp=datetime.utcnow(),
                url=url,
                condition=condition,
                stattrak=stattrak,
                souvenir=souvenir
            )
            
        except Exception as e:
            print(f"Error parsing Steam listing: {e}")
            return None
    
    def _parse_steam_page(self, html: str, skin_id: str) -> Optional[SkinPrice]:
        """Parse Steam market page HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find price element
            price_elem = soup.find('span', {'class': 'market_listing_price'})
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            price = float(re.sub(r'[^\d.]', '', price_text))
            
            # Find item name
            name_elem = soup.find('span', {'id': 'largeiteminfo_item_name'})
            name = name_elem.get_text().strip() if name_elem else ""
            
            # Extract condition and other info
            condition = self._extract_condition(name)
            stattrak = "StatTrak" in name
            souvenir = "Souvenir" in name
            
            url = f"{self.market_url}/listings/730/{skin_id}"
            
            return SkinPrice(
                marketplace="Steam",
                price=price,
                currency="USD",
                available=True,
                listing_count=1,
                timestamp=datetime.utcnow(),
                url=url,
                condition=condition,
                stattrak=stattrak,
                souvenir=souvenir
            )
            
        except Exception as e:
            print(f"Error parsing Steam page: {e}")
            return None
    
    def _extract_condition(self, name: str) -> str:
        """Extract wear condition from skin name"""
        conditions = ["Factory New", "Minimal Wear", "Field-Tested", "Well-Worn", "Battle-Scarred"]
        for condition in conditions:
            if condition in name:
                return condition
        return ""
    
    async def get_fees(self, price: float) -> float:
        """Calculate Steam fees (typically 15%)"""
        return price * 0.15 