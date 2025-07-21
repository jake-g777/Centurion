#!/usr/bin/env python3
"""
Test CSFloat authentication and API access
"""

import asyncio
import sys
import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.marketplaces.csfloat import CSFloatMarketplace

async def test_csfloat_auth():
    """Test different CSFloat authentication approaches"""
    print("Testing CSFloat Authentication")
    print("=" * 40)
    
    # Check if API key is available
    api_key = os.getenv("CSFLOAT_API_KEY")
    if api_key:
        print(f"✅ CSFloat API key found: {api_key[:10]}...")
    else:
        print("❌ No CSFloat API key found in environment")
    
    # Test 1: Direct API call without authentication
    print("\n1. Testing direct API call without auth...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://csfloat.com/api/v1/listings") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Success! Found {len(data.get('data', []))} listings")
                else:
                    print(f"   ❌ Failed: {response.status}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: With API key in Authorization header
    if api_key:
        print(f"\n2. Testing with API key in Authorization header...")
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://csfloat.com/api/v1/listings", headers=headers) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success! Found {len(data.get('data', []))} listings")
                    else:
                        print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 3: With API key as direct header
    if api_key:
        print(f"\n3. Testing with API key as direct header...")
        try:
            headers = {"Authorization": api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://csfloat.com/api/v1/listings", headers=headers) as response:
                    print(f"   Status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Success! Found {len(data.get('data', []))} listings")
                    else:
                        print(f"   ❌ Failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 4: Using the marketplace class
    print(f"\n4. Testing with CSFloatMarketplace class...")
    try:
        csfloat = CSFloatMarketplace()
        results = await csfloat.search_skin("Redline", "AK-47")
        print(f"   Found {len(results)} results")
        if results:
            print(f"   ✅ Success! First result: ${results[0].price:.2f}")
        else:
            print(f"   ❌ No results found")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_csfloat_auth()) 