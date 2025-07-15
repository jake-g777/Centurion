import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
import json
import re
from datetime import datetime
import os

from .base import BaseMarketplace, SkinPrice

class CSFloatMarketplace(BaseMarketplace):
    """CSFloat marketplace scraper"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("CSFLOAT_API_KEY"))
        self.base_url = "https://csfloat.com"
        self.api_url = "https://csfloat.com/api/v1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def search_skin(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Search for a skin on CSFloat"""
        try:
            # Build search query
            query = skin_name
            if weapon:
                query = f"{weapon} {skin_name}"
            
            # Try different CSFloat API endpoints based on common patterns
            endpoints_to_try = [
                f"{self.api_url}/listings",
                f"{self.api_url}/items",
                f"{self.api_url}/search",
                f"{self.base_url}/api/v1/listings",
                f"{self.base_url}/api/v1/items"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    # Try different parameter combinations
                    param_combinations = [
                        {"q": query, "limit": 50, "sort": "price_asc"},
                        {"query": query, "limit": 50, "sort": "price"},
                        {"search": query, "limit": 50},
                        {"name": query, "limit": 50}
                    ]
                    
                    for params in param_combinations:
                        try:
                            # Set up headers with API key if available
                            headers = self.headers.copy()
                            if self.api_key:
                                headers["Authorization"] = self.api_key  # Direct API key, not Bearer
                            
                            async with aiohttp.ClientSession() as session:
                                async with session.get(endpoint, params=params, headers=headers) as response:
                                    print(f"Trying CSFloat endpoint: {endpoint} with params: {params} - Status: {response.status}")
                                    
                                    if response.status == 200:
                                        data = await response.json()
                                        print(f"CSFloat API response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                                        
                                        # CSFloat returns data in a 'data' field
                                        listings = data.get("data", [])
                                        if listings:
                                            print(f"Found {len(listings)} CSFloat listings")
                                            # Debug: show first listing structure
                                            if len(listings) > 0:
                                                print(f"First listing keys: {list(listings[0].keys()) if isinstance(listings[0], dict) else 'Not a dict'}")
                                            return self._parse_listings(listings)
                                        else:
                                            print("No listings found in CSFloat response")
                                            continue
                                    elif response.status == 401:
                                        print(f"CSFloat API unauthorized (401) - API key may be invalid")
                                        continue
                                    elif response.status == 403:
                                        print(f"CSFloat API forbidden (403) - trying different approach")
                                        continue
                                    else:
                                        print(f"CSFloat endpoint {endpoint} failed: {response.status}")
                                        continue
                                        
                        except Exception as e:
                            print(f"Error with CSFloat endpoint {endpoint}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Error trying CSFloat endpoint {endpoint}: {e}")
                    continue
            
            # If all API attempts fail, try web scraping as fallback
            print("All CSFloat API attempts failed, trying web scraping...")
            return await self._search_skin_alternative(skin_name, weapon)
                        
        except Exception as e:
            print(f"Error searching CSFloat: {e}")
            return []
    
    async def _search_skin_alternative(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Alternative search method using web scraping"""
        try:
            # Try using the web interface instead of API
            search_url = f"{self.base_url}/search"
            
            # Build search query
            query = skin_name
            if weapon:
                query = f"{weapon} {skin_name}"
            
            params = {
                "q": query,
                "sort": "price_asc"
            }
            
            # Use a more browser-like user agent
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_html_listings(html)
                    else:
                        print(f"CSFloat alternative search failed: {response.status}")
                        return []
                        
        except Exception as e:
            print(f"Error in CSFloat alternative search: {e}")
            return []
    
    def _parse_html_listings(self, html: str) -> List[SkinPrice]:
        """Parse HTML listings from CSFloat web page"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            soup = BeautifulSoup(html, 'html.parser')
            prices = []
            
            # Look for price elements in the HTML
            # This is a simplified parser - CSFloat's actual structure may vary
            price_elements = soup.find_all('span', class_=re.compile(r'price|cost|amount'))
            
            for elem in price_elements:
                try:
                    price_text = elem.get_text().strip()
                    # Extract price from text (remove $ and commas)
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    if price_match:
                        price = float(price_match.group(1).replace(',', ''))
                        
                        # Try to find item name from nearby elements
                        name_elem = elem.find_parent().find('span', class_=re.compile(r'name|title'))
                        name = name_elem.get_text().strip() if name_elem else "Unknown"
                        
                        prices.append(SkinPrice(
                            marketplace="CSFloat",
                            price=price,
                            currency="USD",
                            available=True,
                            listing_count=1,
                            timestamp=datetime.utcnow(),
                            url="",
                            condition="",
                            stattrak=False,
                            souvenir=False
                        ))
                except Exception as e:
                    continue
            
            return prices
            
        except Exception as e:
            print(f"Error parsing CSFloat HTML: {e}")
            return []
    
    async def get_skin_price(self, skin_id: str) -> Optional[SkinPrice]:
        """Get current price for a specific skin"""
        try:
            url = f"{self.api_url}/listings/{skin_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_listing(data)
                    else:
                        return None
                        
        except Exception as e:
            print(f"Error getting CSFloat price: {e}")
            return None
    
    async def get_popular_skins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of popular skins from CSFloat"""
        try:
            url = f"{self.api_url}/listings"
            params = {
                "limit": limit,
                "sort": "volume_desc"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("listings", [])
                    else:
                        return []
                        
        except Exception as e:
            print(f"Error getting popular skins from CSFloat: {e}")
            return []
    
    def _parse_listings(self, listings: list) -> list:
        """Parse CSFloat listings into SkinPrice objects"""
        prices = []
        print(f"Parsing {len(listings)} CSFloat listings")
        
        for i, listing in enumerate(listings[:3]):  # Only show first 3 for debugging
            try:
                if not isinstance(listing, dict):
                    continue  # skip non-dict entries
                
                # Debug: Print the first few listings to see structure
                if i == 0:
                    print(f"First CSFloat listing keys: {list(listing.keys())}")
                    print(f"Price field: {listing.get('price')}")
                    print(f"Item field: {listing.get('item')}")
                
                # Extract price (should be a dict with 'usd' key, fallback to float/int)
                price_info = listing.get("price", {})
                if isinstance(price_info, dict):
                    price_usd = price_info.get("usd", 0)
                else:
                    price_usd = price_info or 0
                
                if not price_usd:
                    continue
                
                # Extract skin info from CSFloat's actual structure
                item = listing.get("item", {})
                
                # CSFloat uses market_hash_name format: "Item Name (Condition)"
                market_hash_name = item.get("market_hash_name", "")
                item_name = item.get("item_name", "")
                wear_name = item.get("wear_name", "")
                is_stattrak = item.get("is_stattrak", False)
                is_souvenir = item.get("is_souvenir", False)
                
                # Debug: Print item details
                if i == 0:
                    print(f"Market hash name: {market_hash_name}")
                    print(f"Item name: {item_name}")
                    print(f"Wear name: {wear_name}")
                    print(f"Is StatTrak: {is_stattrak}")
                    print(f"Is Souvenir: {is_souvenir}")
                    print(f"Price USD: {price_usd}")
                
                # Build URL
                listing_id = listing.get("id", "")
                url = f"{self.base_url}/item/{listing_id}" if listing_id else ""
                
                prices.append(SkinPrice(
                    marketplace="CSFloat",
                    price=float(price_usd),
                    currency="USD",
                    available=True,
                    listing_count=1,
                    timestamp=datetime.utcnow(),
                    url=url,
                    condition=exterior,
                    stattrak=stattrak,
                    souvenir=souvenir
                ))
            except Exception as e:
                print(f"Error parsing CSFloat listing {i}: {e}")
                continue
        
        print(f"Successfully parsed {len(prices)} CSFloat prices")
        return prices
    
    def _parse_listing(self, listing: Dict) -> Optional[SkinPrice]:
        """Parse a single CSFloat listing"""
        try:
            # Extract basic info
            price_usd = listing.get("price", {}).get("usd", 0)
            if not price_usd:
                return None
            
            # Extract skin info
            item = listing.get("item", {})
            name = item.get("name", "")
            weapon = item.get("weapon", "")
            exterior = item.get("exterior", "")
            stattrak = item.get("stattrak", False)
            souvenir = item.get("souvenir", False)
            
            # Build URL
            listing_id = listing.get("id", "")
            url = f"{self.base_url}/item/{listing_id}" if listing_id else ""
            
            return SkinPrice(
                marketplace="CSFloat",
                price=float(price_usd),
                currency="USD",
                available=True,
                listing_count=1,
                timestamp=datetime.utcnow(),
                url=url,
                condition=exterior,
                stattrak=stattrak,
                souvenir=souvenir
            )
            
        except Exception as e:
            print(f"Error parsing CSFloat listing: {e}")
            return None
    
    async def get_fees(self, price: float) -> float:
        """Calculate CSFloat fees (typically 2.5%)"""
        return price * 0.025 