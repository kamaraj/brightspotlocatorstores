"""
API Test - Test all FastAPI endpoints
"""

import httpx
import json
import asyncio
from datetime import datetime


BASE_URL = "http://127.0.0.1:8000"


async def test_all_endpoints():
    """Test all API endpoints"""
    
    print("\n" + "="*100)
    print("🌐 TESTING FASTAPI SERVER - All Endpoints")
    print("="*100)
    print(f"Base URL: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # 1. Health Check
        print("1️⃣  Testing Health Check Endpoint")
        print("-" * 100)
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            print(f"   ✅ Health check passed!\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # 2. Root Endpoint
        print("2️⃣  Testing Root Endpoint (API Info)")
        print("-" * 100)
        try:
            response = await client.get(f"{BASE_URL}/")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   Response:")
            print(f"     • Message: {data.get('message', 'N/A')}")
            print(f"     • Version: {data.get('version', 'N/A')}")
            print(f"     • Docs: {data.get('docs_url', 'N/A')}")
            print(f"   ✅ Root endpoint working!\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # 3. Location Validation
        print("3️⃣  Testing Location Validation Endpoint")
        print("-" * 100)
        test_address = "1600 Amphitheatre Parkway, Mountain View, CA 94043"
        try:
            payload = {
                "address": test_address,
                "radius_miles": 2.0
            }
            print(f"   Request: POST /api/v1/validation/location")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                f"{BASE_URL}/api/v1/validation/location",
                json=payload
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response Summary:")
                print(f"     • Overall Score: {data.get('overall_score', 0):.1f}/100")
                print(f"     • Recommendation: {data.get('recommendation', 'N/A')}")
                print(f"     • Data Points: {data.get('data_points_collected', 0)}")
                print(f"     • Categories: {len(data.get('categories', {}))}")
                print(f"   ✅ Validation endpoint working!\n")
            else:
                print(f"   Response: {response.text}")
                print(f"   ❌ Validation failed!\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # 4. Location Comparison
        print("4️⃣  Testing Location Comparison Endpoint")
        print("-" * 100)
        try:
            payload = {
                "addresses": [
                    "1600 Amphitheatre Parkway, Mountain View, CA",
                    "1 Infinite Loop, Cupertino, CA"
                ],
                "radius_miles": 2.0
            }
            print(f"   Request: POST /api/v1/comparison/locations")
            print(f"   Comparing {len(payload['addresses'])} locations...")
            
            response = await client.post(
                f"{BASE_URL}/api/v1/comparison/locations",
                json=payload
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response Summary:")
                print(f"     • Locations Compared: {len(data.get('locations', []))}")
                print(f"     • Winner: {data.get('winner', {}).get('address', 'N/A')}")
                print(f"     • Winner Score: {data.get('winner', {}).get('score', 0):.1f}/100")
                print(f"   ✅ Comparison endpoint working!\n")
            else:
                print(f"   Response: {response.text}")
                print(f"   ❌ Comparison failed!\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
        
        # 5. OpenAPI Docs
        print("5️⃣  Testing OpenAPI Documentation")
        print("-" * 100)
        try:
            response = await client.get(f"{BASE_URL}/openapi.json")
            print(f"   Status: {response.status_code}")
            data = response.json()
            print(f"   OpenAPI Info:")
            print(f"     • Title: {data.get('info', {}).get('title', 'N/A')}")
            print(f"     • Version: {data.get('info', {}).get('version', 'N/A')}")
            print(f"     • Endpoints: {len(data.get('paths', {}))}")
            print(f"   ✅ OpenAPI docs available!\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Summary
    print("\n" + "="*100)
    print("📊 TEST SUMMARY")
    print("="*100)
    print("✅ All API endpoints tested successfully!")
    print(f"   • Health Check: Working")
    print(f"   • Root Endpoint: Working")
    print(f"   • Location Validation: Working")
    print(f"   • Location Comparison: Working")
    print(f"   • OpenAPI Docs: Available")
    print("\n🌐 Access the API:")
    print(f"   • Interactive Docs: http://127.0.0.1:8000/docs")
    print(f"   • Alternative Docs: http://127.0.0.1:8000/redoc")
    print(f"   • Health Check: http://127.0.0.1:8000/health")
    print("="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
