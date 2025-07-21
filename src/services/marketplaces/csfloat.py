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
            self.headers["Authorization"] = self.api_key  # Direct API key format
    
    async def search_skin(self, skin_name: str, weapon: str = None) -> List[SkinPrice]:
        """Search for a skin on CSFloat"""
        try:
            print(f"Searching CSFloat for: {weapon} {skin_name}")
            
            # CSFloat API doesn't support search parameters well, so we get all listings and filter client-side
            # Try to get more listings by using pagination
            endpoint = f"{self.api_url}/listings"
            params = {"limit": 100}  # Try to get more listings
            
            # Use the headers already set up in __init__
            headers = self.headers.copy()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers=headers) as response:
                    print(f"CSFloat API request to {endpoint} - Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"CSFloat API response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        # CSFloat returns data in a 'data' field
                        listings = data.get("data", [])
                        if listings:
                            print(f"Found {len(listings)} total CSFloat listings")
                            # Debug: show first listing structure
                            if len(listings) > 0:
                                print(f"First listing keys: {list(listings[0].keys()) if isinstance(listings[0], dict) else 'Not a dict'}")
                            
                            # Debug: Show some sample items to see what's available
                            print("\nSample items from CSFloat:")
                            for i, listing in enumerate(listings[:5]):
                                item = listing.get("item", {})
                                market_hash_name = item.get("market_hash_name", "Unknown")
                                print(f"  {i+1}. {market_hash_name}")
                            
                            return self._parse_listings(listings, weapon, skin_name)
                        else:
                            print("No listings found in CSFloat response")
                            return []
                    elif response.status == 401:
                        print(f"CSFloat API unauthorized (401) - API key may be invalid")
                        return []
                    elif response.status == 403:
                        print(f"CSFloat API forbidden (403) - API key required or invalid")
                        return []
                    else:
                        print(f"CSFloat API failed: {response.status}")
                        return []
                        
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
    
    def _parse_listings(self, listings: list, target_weapon: str = None, target_skin: str = None) -> list:
        """Parse CSFloat listings into SkinPrice objects"""
        prices = []
        print(f"Parsing {len(listings)} CSFloat listings")
        
        for i, listing in enumerate(listings):
            try:
                if not isinstance(listing, dict):
                    continue  # skip non-dict entries
                
                # Debug: Print the first few listings to see structure
                if i < 3:
                    print(f"CSFloat listing {i} keys: {list(listing.keys())}")
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
                
                # Debug: Print item details for first few items
                if i < 3:
                    print(f"Market hash name: {market_hash_name}")
                    print(f"Item name: {item_name}")
                    print(f"Wear name: {wear_name}")
                    print(f"Is StatTrak: {is_stattrak}")
                    print(f"Is Souvenir: {is_souvenir}")
                    print(f"Price USD: {price_usd}")
                
                # Filter by weapon and skin if specified
                if target_weapon and target_skin:
                    # Check if the item matches our target weapon and skin
                    item_matches = False
                    
                    # Check market_hash_name (most reliable)
                    if market_hash_name:
                        # Look for weapon name and skin name in market_hash_name
                        weapon_lower = target_weapon.lower()
                        skin_lower = target_skin.lower()
                        market_hash_lower = market_hash_name.lower()
                        
                        if weapon_lower in market_hash_lower and skin_lower in market_hash_lower:
                            item_matches = True
                    
                    # Also check item_name as fallback
                    if not item_matches and item_name:
                        weapon_lower = target_weapon.lower()
                        skin_lower = target_skin.lower()
                        item_name_lower = item_name.lower()
                        
                        if weapon_lower in item_name_lower and skin_lower in item_name_lower:
                            item_matches = True
                    
                    # Skip items that don't match our target
                    if not item_matches:
                        continue
                
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
                    condition=wear_name,
                    stattrak=is_stattrak,
                    souvenir=is_souvenir
                ))
            except Exception as e:
                print(f"Error parsing CSFloat listing {i}: {e}")
                continue
        
        print(f"Successfully parsed {len(prices)} CSFloat prices (filtered for {target_weapon} {target_skin})")
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