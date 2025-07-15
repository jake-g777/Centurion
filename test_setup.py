#!/usr/bin/env python3
"""
Test script to verify the CS2 Arbitrage Tool setup
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
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ Pandas imported successfully")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"✗ BeautifulSoup import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test if the project structure is correct"""
    print("\nTesting project structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "env.example",
        "src/__init__.py",
        "src/models/__init__.py",
        "src/models/skin.py",
        "src/database/__init__.py",
        "src/database/database.py",
        "src/services/__init__.py",
        "src/services/price_monitor.py",
        "src/services/marketplaces/__init__.py",
        "src/services/marketplaces/base.py",
        "src/services/marketplaces/csfloat.py",
        "src/services/marketplaces/steam.py",
        "src/api/__init__.py",
        "src/api/routes.py",
        "src/web/__init__.py",
        "src/web/routes.py",
        "src/web/templates/base.html",
        "src/web/templates/dashboard.html"
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

async def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from src.database.database import init_db, get_db
        from src.models.skin import Base
        
        # Initialize database
        await init_db()
        print("✓ Database initialized successfully")
        
        # Test session creation
        db_gen = get_db()
        db = next(db_gen)
        print("✓ Database session created successfully")
        
        # Close session
        db.close()
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
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
    print("CS2 Arbitrage Tool - Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Project Structure Test", test_project_structure),
        ("Marketplace Initialization Test", test_marketplace_initialization),
        ("Database Connection Test", test_database_connection),
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
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Copy env.example to .env and configure your API keys")
        print("2. Run: python main.py")
        print("3. Open http://localhost:8000 in your browser")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 