#!/usr/bin/env python3
"""
Test upload functionality locally
"""
import requests
import tempfile
import os

def test_local_upload():
    """Test the local upload endpoint"""
    url = "http://localhost:5001/api/upload"
    
    # Create test CSV content
    test_csv = """address,trademe_url
"123 Queen Street, Auckland","https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/cbd/listing/1234567890"
"456 Ponsonby Road, Auckland","https://www.trademe.co.nz/a/property/residential/sale/auckland/auckland-city/ponsonby/listing/0987654321"
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(test_csv)
        temp_file = f.name
    
    try:
        print(f"🧪 Testing local upload endpoint: {url}")
        
        # Test upload
        with open(temp_file, 'rb') as f:
            files = {"file": ("test.csv", f, "text/csv")}
            response = requests.post(url, files=files)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Local upload successful!")
            data = response.json()
            print(f"📈 Properties processed: {data.get('total', 0)}")
        else:
            print("❌ Local upload failed!")
            print(f"🔍 Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to localhost:5001")
        print("💡 Make sure the local server is running with: python run_local.py")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    test_local_upload()
