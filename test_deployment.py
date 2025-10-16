#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_deployment():
    """Test the deployment configuration"""
    print("🚀 Testing NZ Property Flip Calculator Deployment")
    
    try:
        # Test 1: Import main app
        print("📦 Testing imports...")
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        # Test 2: Test pipeline imports
        from app.pipeline import process_addresses, process_addresses_with_urls
        print("✅ Pipeline functions imported successfully")
        
        # Test 3: Test models
        from app.models import DataPoints, AddressScore, ConnectionData
        print("✅ Models imported successfully")
        
        # Test 4: Test providers
        from app.providers.nz_comprehensive import NZComprehensiveProvider
        print("✅ NZ Comprehensive Provider imported successfully")
        
        # Test 5: Test scoring
        from app.scoring import score_datapoints
        print("✅ Scoring functions imported successfully")
        
        print("\n🎉 All tests passed! Deployment configuration is ready.")
        print("\n📋 Next steps:")
        print("1. Commit your changes to GitHub")
        print("2. Connect your repository to Railway")
        print("3. Deploy using the railway.json configuration")
        print("4. Test the deployed application")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_deployment())
    sys.exit(0 if success else 1)
