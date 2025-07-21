#!/usr/bin/env python3
"""
Test CSFloat filtering for specific weapon skins
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.marketplaces.csfloat import CSFloatMarketplace

async def test_csfloat_filtering():
    """Test CSFloat filtering for AK-47 Redline"""
    print("Testing CSFloat Filtering for AK-47 Redline")
    print("=" * 50)
    
    # Initialize CSFloat marketplace
    csfloat = CSFloatMarketplace()
    
    # Test search for AK-47 Redline
    print("Searching for AK-47 Redline on CSFloat...")
    results = await csfloat.search_skin("Redline", "AK-47")
    
    print(f"\nFound {len(results)} AK-47 Redline items:")
    print("-" * 30)
    
    for i, price in enumerate(results[:10]):  # Show first 10 results
        print(f"{i+1}. {price.marketplace} - ${price.price:.2f}")
        print(f"   Condition: {price.condition}")
        print(f"   StatTrak: {price.stattrak}")
        print(f"   Souvenir: {price.souvenir}")
        print(f"   URL: {price.url}")
        print()
    
    if not results:
        print("❌ No AK-47 Redline items found!")
        print("This means the filtering isn't working properly.")
    else:
        print("✅ CSFloat filtering is working!")
        print(f"Found {len(results)} AK-47 Redline items")

if __name__ == "__main__":
    asyncio.run(test_csfloat_filtering()) 