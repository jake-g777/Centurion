#!/usr/bin/env python3
"""
Test script for marketplace integrations
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.price_monitor_simple import SimplePriceMonitor
from services.marketplaces.steam import SteamMarketplace
from services.marketplaces.csfloat import CSFloatMarketplace

async def test_ak47_redline_comparison():
    """Test AK-47 Redline price comparison by wear condition"""
    print("🎯 Testing AK-47 Redline Price Comparison by Wear Condition")
    print("=" * 60)
    
    # Initialize marketplaces
    steam = SteamMarketplace()
    csfloat = CSFloatMarketplace()
    
    # Test AK-47 Redline specifically
    weapon = "AK-47"
    skin = "Redline"
    
    print(f"\n🔍 Searching for: {weapon} | {skin}")
    print("-" * 40)
    
    # Get Steam prices
    print("\n📈 Steam Marketplace:")
    steam_prices = await steam.search_skin(skin, weapon)
    
    # Group Steam prices by condition and find lowest for each
    steam_by_condition = {}
    for price in steam_prices:
        condition = price.condition or "Unknown"
        if condition not in steam_by_condition or price.price < steam_by_condition[condition].price:
            steam_by_condition[condition] = price
    
    # Display Steam results
    for condition in sorted(steam_by_condition.keys()):
        price = steam_by_condition[condition]
        stattrak_text = " ⭐" if price.stattrak else ""
        print(f"   {condition}: ${price.price:.2f}{stattrak_text}")
    
    # Get CSFloat prices
    print("\n📉 CSFloat Marketplace:")
    csfloat_prices = await csfloat.search_skin(skin, weapon)
    
    # Group CSFloat prices by condition and find lowest for each
    csfloat_by_condition = {}
    for price in csfloat_prices:
        condition = price.condition or "Unknown"
        if condition not in csfloat_by_condition or price.price < csfloat_by_condition[condition].price:
            csfloat_by_condition[condition] = price
    
    # Display CSFloat results
    for condition in sorted(csfloat_by_condition.keys()):
        price = csfloat_by_condition[condition]
        stattrak_text = " ⭐" if price.stattrak else ""
        print(f"   {condition}: ${price.price:.2f}{stattrak_text}")
    
    # Compare prices and find arbitrage opportunities
    print("\n💰 Arbitrage Analysis:")
    print("-" * 40)
    
    arbitrage_found = False
    
    # Check Steam -> CSFloat arbitrage
    for condition in steam_by_condition:
        if condition in csfloat_by_condition:
            steam_price = steam_by_condition[condition]
            csfloat_price = csfloat_by_condition[condition]
            
            # Calculate potential profit (Steam buy, CSFloat sell)
            profit = csfloat_price.price - steam_price.price
            profit_percent = (profit / steam_price.price) * 100 if steam_price.price > 0 else 0
            
            if profit > 0:
                arbitrage_found = True
                print(f"   📈 Buy Steam {condition}: ${steam_price.price:.2f}")
                print(f"   📉 Sell CSFloat {condition}: ${csfloat_price.price:.2f}")
                print(f"   💵 Potential Profit: ${profit:.2f} ({profit_percent:.1f}%)")
                print()
    
    # Check CSFloat -> Steam arbitrage
    for condition in csfloat_by_condition:
        if condition in steam_by_condition:
            csfloat_price = csfloat_by_condition[condition]
            steam_price = steam_by_condition[condition]
            
            # Calculate potential profit (CSFloat buy, Steam sell)
            profit = steam_price.price - csfloat_price.price
            profit_percent = (profit / csfloat_price.price) * 100 if csfloat_price.price > 0 else 0
            
            if profit > 0:
                arbitrage_found = True
                print(f"   📈 Buy CSFloat {condition}: ${csfloat_price.price:.2f}")
                print(f"   📉 Sell Steam {condition}: ${steam_price.price:.2f}")
                print(f"   💵 Potential Profit: ${profit:.2f} ({profit_percent:.1f}%)")
                print()
    
    if not arbitrage_found:
        print("   ❌ No arbitrage opportunities found")
    
    print("\n" + "=" * 60)

async def main():
    """Main test function"""
    print("🚀 Starting AK-47 Redline Price Comparison Test...")
    print()
    
    try:
        await test_ak47_redline_comparison()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 