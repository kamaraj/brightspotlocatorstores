"""
Simple API Test - ASCII only output
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_apis():
    print("="*60)
    print("API KEYS TEST")
    print("="*60)
    
    # Test Google Geocoding
    print("\n[1] Testing Google Geocoding API...")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    print(f"    Key: {api_key[:20]}..." if api_key else "    Key: NOT FOUND")
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": "1600 Amphitheatre Parkway, Mountain View, CA", "key": api_key}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            print(f"    Status: {data.get('status')}")
            if "error_message" in data:
                print(f"    Error: {data['error_message']}")
            if data.get("status") == "OK":
                print("    Result: SUCCESS")
            else:
                print("    Result: FAILED")
    except Exception as e:
        print(f"    Exception: {e}")
    
    # Test Census API
    print("\n[2] Testing Census API...")
    census_key = os.getenv("CENSUS_API_KEY")
    print(f"    Key: {census_key[:20]}..." if census_key else "    Key: NOT FOUND")
    
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": "B01003_001E",
        "for": "tract:*",
        "in": "state:06 county:085",
        "key": census_key
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            print(f"    Status Code: {response.status_code}")
            if response.status_code == 200:
                print("    Result: SUCCESS")
            else:
                print(f"    Result: FAILED - {response.text[:100]}")
    except Exception as e:
        print(f"    Exception: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(test_apis())
