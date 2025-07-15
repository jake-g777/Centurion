#!/usr/bin/env python3
"""
Test script to check marketplace data retrieval
"""

import asyncio
import os
from dotenv import load_dotenv
from src.services.price_monitor_simple import SimplePriceMonitor

# Load environment variables
load_dotenv()

async def test_marketplace_data():
    """Test getting data from both Steam and CSFloat"""
    
    print("🔍 Testing Marketplace Data Retrieval")
    print("=" * 50)
    
    # Initialize price monitor
    price_monitor = SimplePriceMonitor()
    
    # Test skins
    test_cases = [
        {"weapon": "AK-47", "skin": "Redline"},
        {"weapon": "AWP", "skin": "Asiimov"},
        {"weapon": "M4A4", "skin": "Asiimov"},
        {"weapon": "Desert Eagle", "skin": "Blaze"},
    ]
    
    for test_case in test_cases:
        weapon = test_case["weapon"]
        skin = test_case["skin"]
        
        print(f"\n🎯 Testing: {weapon} | {skin}")
        print("-" * 30)
        
        try:
            # Search for the skin
            prices = await price_monitor.search_skin_manual(skin, weapon)
            
            if not prices:
                print("❌ No prices found")
                continue
            
            # Group by marketplace
            marketplace_prices = {}
            for price in prices:
                if price.marketplace not in marketplace_prices:
                    marketplace_prices[price.marketplace] = []
                marketplace_prices[price.marketplace].append(price)
            
            # Display results
            for marketplace, price_list in marketplace_prices.items():
                print(f"✅ {marketplace}: {len(price_list)} listings found")
                
                # Show lowest price
                lowest_price = min(p.price for p in price_list)
                print(f"   💰 Lowest: ${lowest_price:.2f}")
                
                # Show price range
                highest_price = max(p.price for p in price_list)
                if highest_price != lowest_price:
                    print(f"   📊 Range: ${lowest_price:.2f} - ${highest_price:.2f}")
                
                # Show conditions available
                conditions = set(p.condition for p in price_list if p.condition)
                if conditions:
                    print(f"   🎨 Conditions: {', '.join(conditions)}")
                
                # Show StatTrak options
                stattrak_count = sum(1 for p in price_list if p.stattrak)
                if stattrak_count > 0:
                    print(f"   ⭐ StatTrak: {stattrak_count} listings")
            
            # Check for arbitrage opportunities
            opportunities = await price_monitor.find_arbitrage_opportunities(skin, weapon)
            if opportunities:
                print(f"💰 Arbitrage Opportunities: {len(opportunities)} found")
                for opp in opportunities:
                    print(f"   📈 Buy: {opp['buy_marketplace']} @ ${opp['buy_price']:.2f}")
                    print(f"   📉 Sell: {opp['sell_marketplace']} @ ${opp['sell_price']:.2f}")
                    print(f"   💵 Profit: ${opp['net_profit']:.2f} ({opp['profit_percentage']:.1f}%)")
            else:
                print("❌ No arbitrage opportunities found")
                
        except Exception as e:
            print(f"❌ Error testing {weapon} {skin}: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

async def test_marketplace_status():
    """Test marketplace availability"""
    
    print("\n🔧 Testing Marketplace Status")
    print("=" * 30)
    
    price_monitor = SimplePriceMonitor()
    
    try:
        status = await price_monitor.get_marketplace_status()
        
        for mp in status:
            status_icon = "✅" if mp["available"] else "❌"
            print(f"{status_icon} {mp['name']}: {'Online' if mp['available'] else 'Offline'}")
            
    except Exception as e:
        print(f"❌ Error checking marketplace status: {e}")

if __name__ == "__main__":
    print("🚀 Starting Marketplace Tests...")
    asyncio.run(test_marketplace_status())
    asyncio.run(test_marketplace_data()) 