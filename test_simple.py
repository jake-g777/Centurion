#!/usr/bin/env python3
"""
Test script for the simplified CS2 Arbitrage Tool (no database)
"""

import sys
import os
import asyncio
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✓ aiohttp imported successfully")
    except ImportError as e:
        print(f"✗ aiohttp import failed: {e}")
        return False
    
    try:
        import httpx
        print("✓ httpx imported successfully")
    except ImportError as e:
        print(f"✗ httpx import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"✗ BeautifulSoup import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if the simplified project structure is correct"""
    print("\nTesting project structure...")
    
    required_files = [
        "main_simple.py",
        "requirements.txt",
        "README.md",
        "env.example",
        "src/__init__.py",
        "src/services/__init__.py",
        "src/services/price_monitor_simple.py",
        "src/services/marketplaces/__init__.py",
        "src/services/marketplaces/base.py",
        "src/services/marketplaces/csfloat.py",
        "src/services/marketplaces/steam.py",
        "src/api/__init__.py",
        "src/api/routes_simple.py",
        "src/web/__init__.py",
        "src/web/routes_simple.py",
        "src/web/templates/base.html",
        "src/web/templates/dashboard_simple.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n✗ Missing files: {missing_files}")
        return False
    
    return True

async def test_marketplace_initialization():
    """Test if marketplaces can be initialized"""
    print("\nTesting marketplace initialization...")
    
    try:
        from src.services.marketplaces.csfloat import CSFloatMarketplace
        from src.services.marketplaces.steam import SteamMarketplace
        
        csfloat = CSFloatMarketplace()
        steam = SteamMarketplace()
        
        print(f"✓ CSFloat marketplace initialized: {csfloat}")
        print(f"✓ Steam marketplace initialized: {steam}")
        
        return True
    except Exception as e:
        print(f"✗ Marketplace initialization failed: {e}")
        return False

async def test_price_monitor():
    """Test if the simple price monitor can be initialized"""
    print("\nTesting price monitor initialization...")
    
    try:
        from src.services.price_monitor_simple import SimplePriceMonitor
        
        monitor = SimplePriceMonitor()
        print(f"✓ SimplePriceMonitor initialized: {monitor}")
        print(f"✓ Marketplaces loaded: {len(monitor.marketplaces)}")
        
        return True
    except Exception as e:
        print(f"✗ Price monitor initialization failed: {e}")
        return False

def test_environment_setup():
    """Test environment setup"""
    print("\nTesting environment setup...")
    
    # Check if env.example exists
    if not Path("env.example").exists():
        print("✗ env.example file not found")
        return False
    
    print("✓ env.example file found")
    
    # Check if .env exists (optional)
    if Path(".env").exists():
        print("✓ .env file found")
    else:
        print("⚠ .env file not found (you may want to create one from env.example)")
    
    return True

async def main():
    """Run all tests"""
    print("CS2 Arbitrage Tool (Simple) - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Project Structure Test", test_project_structure),
        ("Marketplace Initialization Test", test_marketplace_initialization),
        ("Price Monitor Test", test_price_monitor),
        ("Environment Setup Test", test_environment_setup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your simplified setup is ready.")
        print("\nNext steps:")
        print("1. Copy env.example to .env (optional)")
        print("2. Run: python main_simple.py")
        print("3. Open http://localhost:8000 in your browser")
        print("\nThis version works without a database - perfect for testing!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 