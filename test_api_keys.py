"""
Test API Keys Configuration
Quick script to verify all API keys are working
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_google_geocoding():
    """Test Google Geocoding API"""
    print("\n=== Testing Google Geocoding API ===")
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in environment")
        return False
    
    print(f"[OK] API Key found: {api_key[:20]}...")
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": "1600 Amphitheatre Parkway, Mountain View, CA",
        "key": api_key
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Status: {data.get('status')}")
            
            if data.get("status") == "OK":
                location = data["results"][0]["geometry"]["location"]
                print(f"✅ Geocoding SUCCESS: {location}")
                return True
            else:
                print(f"❌ Geocoding FAILED: {data.get('status')}")
                if "error_message" in data:
                    print(f"   Error: {data['error_message']}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


async def test_google_places():
    """Test Google Places API"""
    print("\n=== Testing Google Places API ===")
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY not found in environment")
        return False
    
    print(f"✓ API Key found: {api_key[:20]}...")
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": "37.4224764,-122.0842499",  # Google HQ
        "radius": 1000,
        "keyword": "daycare",
        "key": api_key
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Status: {data.get('status')}")
            
            if data.get("status") == "OK" or data.get("status") == "ZERO_RESULTS":
                print(f"✅ Places API SUCCESS: Found {len(data.get('results', []))} results")
                return True
            else:
                print(f"❌ Places API FAILED: {data.get('status')}")
                if "error_message" in data:
                    print(f"   Error: {data['error_message']}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


async def test_census_api():
    """Test Census API"""
    print("\n=== Testing Census API ===")
    
    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        print("❌ CENSUS_API_KEY not found in environment")
        return False
    
    print(f"✓ API Key found: {api_key[:20]}...")
    
    # Test with a simple query
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": "B01003_001E",  # Total population
        "for": "tract:*",
        "in": "state:06 county:085",  # Santa Clara County, CA
        "key": api_key
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Census API SUCCESS: Retrieved {len(data)-1} tracts")
                return True
            else:
                print(f"❌ Census API FAILED: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


async def main():
    """Run all API tests"""
    print("=" * 60)
    print("API KEYS VERIFICATION TEST")
    print("=" * 60)
    
    results = {
        "Google Geocoding": await test_google_geocoding(),
        "Google Places": await test_google_places(),
        "Census API": await test_census_api()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for api, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {api}: {'WORKING' if status else 'FAILED'}")
    
    all_working = all(results.values())
    
    if all_working:
        print("\n🎉 All APIs are working correctly!")
    else:
        print("\n⚠️  Some APIs are not working. Please check:")
        print("   1. API keys are correct in .env file")
        print("   2. APIs are enabled in Google Cloud Console:")
        print("      - Geocoding API")
        print("      - Places API")
        print("      - Distance Matrix API")
        print("   3. Census API key is valid")


if __name__ == "__main__":
    asyncio.run(main())
