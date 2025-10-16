#!/usr/bin/env python3
"""
Test script for concurrent browser functionality
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.providers.concurrent_browser_manager import ConcurrentBrowserManager
from app.models import DataPoints

async def test_concurrent_browsers():
    """Test concurrent browser functionality with multiple URLs"""
    
    # Test URLs (using the same URL multiple times for testing)
    test_urls = [
        "https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/avondale/listing/5571595092?rsqid=60e50adfc0a84c759b42f4d526d06966-001",
        "https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/avondale/listing/5571595092?rsqid=60e50adfc0a84c759b42f4d526d06966-001",
        "https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/avondale/listing/5571595092?rsqid=60e50adfc0a84c759b42f4d526d06966-001",
        "https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/avondale/listing/5571595092?rsqid=60e50adfc0a84c759b42f4d526d06966-001",
        "https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/avondale/listing/5571595092?rsqid=60e50adfc0a84c759b42f4d526d06966-001"
    ]
    
    print("🚀 Testing Concurrent Browser Manager")
    print(f"📊 Testing with {len(test_urls)} concurrent requests")
    
    # Initialize concurrent browser manager
    browser_manager = ConcurrentBrowserManager(max_concurrent_browsers=5)
    
    try:
        # Test concurrent fetching
        start_time = asyncio.get_event_loop().time()
        
        tasks = []
        for i, url in enumerate(test_urls):
            task = browser_manager.fetch_with_browser(
                address=f"Test Address {i+1}",
                url=url,
                site_name="TradeMe",
                browser_id=i % 5  # Distribute across browsers
            )
            tasks.append(task)
        
        print("⏳ Starting concurrent browser requests...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        print(f"✅ Completed {len(results)} requests in {total_time:.2f} seconds")
        print(f"📈 Average time per request: {total_time/len(results):.2f} seconds")
        
        # Display results
        successful_results = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Request {i+1} failed: {result}")
            else:
                successful_results += 1
                print(f"✅ Request {i+1} succeeded:")
                print(f"   Address: {result.address}")
                print(f"   Valuation: ${result.current_valuation_mid:,.0f}" if result.current_valuation_mid else "   Valuation: No data")
                print(f"   Method of Sale: {result.method_of_sale or 'Not specified'}")
                print(f"   Source: {result.valuation_source}")
                print()
        
        print(f"📊 Success Rate: {successful_results}/{len(results)} ({successful_results/len(results)*100:.1f}%)")
        
        # Get browser status
        status = await browser_manager.get_browser_status()
        print(f"🔧 Browser Status:")
        print(f"   Total Browsers: {status['total_browsers']}")
        print(f"   Active Browsers: {status['active_browsers']}")
        print(f"   Available Slots: {status['available_slots']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("🧹 Cleaning up browser instances...")
        await browser_manager.close_all_browsers()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    asyncio.run(test_concurrent_browsers())
