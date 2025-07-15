#!/usr/bin/env python3
"""
CS2 Arbitrage Tool - Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "aiohttp",
        "sqlalchemy",
        "pandas",
        "beautifulsoup4",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check environment setup"""
    print("\nChecking environment...")
    
    if not Path("env.example").exists():
        print("❌ env.example file not found")
        return False
    
    if not Path(".env").exists():
        print("⚠ .env file not found")
        print("Creating .env from env.example...")
        try:
            with open("env.example", "r") as f:
                env_content = f.read()
            with open(".env", "w") as f:
                f.write(env_content)
            print("✓ Created .env file")
            print("⚠ Please edit .env file with your API keys before running")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("✓ .env file found")
    
    return True

def run_tests():
    """Run setup tests"""
    print("\nRunning setup tests...")
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def start_application():
    """Start the application"""
    print("\nStarting CS2 Arbitrage Tool...")
    print("=" * 50)
    
    try:
        # Start the FastAPI application
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")

def main():
    """Main startup function"""
    print("CS2 Arbitrage Tool - Startup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check environment
    if not check_environment():
        return 1
    
    # Run tests
    if not run_tests():
        print("\n❌ Setup tests failed. Please fix the issues above.")
        return 1
    
    print("\n🎉 Setup complete! Starting application...")
    
    # Start the application
    start_application()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 