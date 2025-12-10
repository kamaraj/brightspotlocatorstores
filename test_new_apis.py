"""
Test New API Integrations - EPA, HUD, FBI Crime, FEMA
Tests the 4 new data collectors with real locations
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.data_collectors.epa_collector import EPACollector
from app.core.data_collectors.hud_collector import HUDCollector
from app.core.data_collectors.fbi_crime_collector import FBICrimeCollector
from app.core.data_collectors.fema_flood_collector import FEMAFloodCollector
from app.config import get_settings


async def test_epa_collector():
    """Test EPA Envirofacts API"""
    print("\n" + "="*80)
    print("🌍 Testing EPA Envirofacts API")
    print("="*80)
    
    collector = EPACollector()
    
    # Test location: North Lauderdale, FL
    address = "North Lauderdale, FL 33068"
    latitude = 26.2173
    longitude = -80.2259
    
    print(f"📍 Location: {address}")
    print(f"📍 Coordinates: {latitude}, {longitude}")
    print(f"⏳ Fetching EPA data...")
    
    result = await collector.collect(address, latitude, longitude, radius_miles=5)
    
    print(f"\n✅ EPA Data Retrieved:")
    print(f"   TRI Sites: {result.get('tri_sites_count', 0)}")
    print(f"   Superfund Sites: {result.get('superfund_sites_count', 0)}")
    print(f"   Air Facilities: {result.get('air_facilities_count', 0)}")
    print(f"   Air Quality Index: {result.get('air_quality_index', 0):.1f}")
    print(f"   Environmental Hazards Score: {result.get('environmental_hazards_score', 0):.1f}")
    print(f"   Pollution Risk: {result.get('pollution_risk', 'Unknown')}")
    print(f"   Confidence: {result.get('confidence', 'UNKNOWN')}")
    
    return result


async def test_hud_collector():
    """Test HUD User API"""
    print("\n" + "="*80)
    print("🏠 Testing HUD User API")
    print("="*80)
    
    settings = get_settings()
    collector = HUDCollector(api_key=settings.hud_api_key if hasattr(settings, 'hud_api_key') else None)
    
    # Test location: North Lauderdale, FL
    address = "North Lauderdale, FL 33068"
    zip_code = "33068"
    state = "FL"
    
    print(f"📍 Location: {address}")
    print(f"📍 ZIP: {zip_code}, State: {state}")
    print(f"⏳ Fetching HUD Fair Market Rent data...")
    
    result = await collector.collect(address, zip_code, state)
    
    print(f"\n✅ HUD Data Retrieved:")
    print(f"   Studio FMR: ${result.get('fmr_studio', 0):.0f}/month")
    print(f"   1BR FMR: ${result.get('fmr_1br', 0):.0f}/month")
    print(f"   2BR FMR: ${result.get('fmr_2br', 0):.0f}/month")
    print(f"   3BR FMR: ${result.get('fmr_3br', 0):.0f}/month")
    print(f"   Average FMR: ${result.get('average_fmr', 0):.0f}/month")
    print(f"   Real Estate Cost: ${result.get('real_estate_cost_per_sqft', 0):.2f}/sqft")
    print(f"   Estimated Startup: ${result.get('estimated_startup_cost', 0):,.0f}")
    print(f"   Data Year: {result.get('year', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 'UNKNOWN')}")
    
    return result


async def test_fbi_crime_collector():
    """Test FBI Crime Data Explorer API"""
    print("\n" + "="*80)
    print("🚔 Testing FBI Crime Data Explorer API")
    print("="*80)
    
    settings = get_settings()
    collector = FBICrimeCollector(api_key=settings.fbi_crime_api_key if hasattr(settings, 'fbi_crime_api_key') else None)
    
    # Test location: North Lauderdale, FL
    address = "North Lauderdale, FL 33068"
    state = "FL"
    county = "Broward"
    latitude = 26.2173
    longitude = -80.2259
    
    print(f"📍 Location: {address}")
    print(f"📍 State: {state}, County: {county}")
    print(f"⏳ Fetching FBI crime data...")
    
    result = await collector.collect(address, state, county, latitude, longitude)
    
    print(f"\n✅ FBI Crime Data Retrieved:")
    print(f"   Violent Crime Rate: {result.get('violent_crime_rate', 0):.1f} per 100k")
    print(f"   Property Crime Rate: {result.get('property_crime_rate', 0):.1f} per 100k")
    print(f"   Crime Rate Index: {result.get('crime_rate_index', 0):.1f}/100")
    print(f"   Safety Score: {result.get('neighborhood_safety_score', 0):.1f}/100")
    print(f"   Risk Level: {result.get('risk_level', 'Unknown')}")
    print(f"   Data Year: {result.get('data_year', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 'UNKNOWN')}")
    
    return result


async def test_fema_flood_collector():
    """Test FEMA Flood Maps API"""
    print("\n" + "="*80)
    print("🌊 Testing FEMA Flood Maps API")
    print("="*80)
    
    collector = FEMAFloodCollector()
    
    # Test location: North Lauderdale, FL (coastal area)
    address = "North Lauderdale, FL 33068"
    latitude = 26.2173
    longitude = -80.2259
    
    print(f"📍 Location: {address}")
    print(f"📍 Coordinates: {latitude}, {longitude}")
    print(f"⏳ Fetching FEMA flood zone data...")
    
    result = await collector.collect(address, latitude, longitude)
    
    print(f"\n✅ FEMA Flood Data Retrieved:")
    print(f"   Flood Zone: {result.get('flood_zone', 'Unknown')}")
    print(f"   Flood Zone Subtype: {result.get('flood_zone_subtype', 'N/A')}")
    print(f"   Base Flood Elevation: {result.get('base_flood_elevation', 0):.1f} ft")
    print(f"   Flood Risk Score: {result.get('flood_risk_score', 0):.1f}/100")
    print(f"   Risk Level: {result.get('flood_risk_level', 'Unknown')}")
    print(f"   Insurance Required: {result.get('insurance_required', False)}")
    print(f"   SFHA: {result.get('special_flood_hazard_area', False)}")
    print(f"   Confidence: {result.get('confidence', 'UNKNOWN')}")
    
    return result


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 Testing New API Integrations - EPA, HUD, FBI Crime, FEMA")
    print("="*80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test each collector
    try:
        epa_result = await test_epa_collector()
        hud_result = await test_hud_collector()
        fbi_result = await test_fbi_crime_collector()
        fema_result = await test_fema_flood_collector()
        
        # Summary
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        
        total_apis = 4
        successful_apis = 0
        
        if epa_result.get('confidence') == 'HIGH':
            successful_apis += 1
            print("✅ EPA Envirofacts: SUCCESS (real data)")
        else:
            print("⚠️ EPA Envirofacts: Using fallback data")
        
        if hud_result.get('confidence') == 'HIGH':
            successful_apis += 1
            print("✅ HUD User API: SUCCESS (real data)")
        else:
            print("⚠️ HUD User API: Using fallback data (register at https://www.huduser.gov/portal/dataset/fmr-api.html)")
        
        if fbi_result.get('confidence') == 'HIGH':
            successful_apis += 1
            print("✅ FBI Crime Data Explorer: SUCCESS (real data)")
        elif fbi_result.get('confidence') == 'MEDIUM':
            successful_apis += 0.5
            print("⚠️ FBI Crime Data Explorer: State-level data (register at https://api.data.gov/signup/ for agency-level)")
        else:
            print("⚠️ FBI Crime Data Explorer: Using fallback data")
        
        if fema_result.get('confidence') == 'HIGH':
            successful_apis += 1
            print("✅ FEMA Flood Maps: SUCCESS (real data)")
        else:
            print("⚠️ FEMA Flood Maps: Using fallback data")
        
        print(f"\n🎯 Success Rate: {successful_apis}/{total_apis} APIs ({successful_apis/total_apis*100:.0f}%)")
        
        # Calculate new real data percentage
        new_real_points = 0
        if epa_result.get('confidence') == 'HIGH':
            new_real_points += 3  # AQI, hazards, pollution risk
        if hud_result.get('confidence') == 'HIGH':
            new_real_points += 5  # FMR, costs
        if fbi_result.get('confidence') in ['HIGH', 'MEDIUM']:
            new_real_points += 9  # Crime rates
        if fema_result.get('confidence') == 'HIGH':
            new_real_points += 3  # Flood zone, risk
        
        previous_real = 45  # Google + Census
        total_points = 66
        new_total_real = previous_real + new_real_points
        
        print(f"\n📈 Data Coverage:")
        print(f"   Before: {previous_real}/{total_points} points ({previous_real/total_points*100:.0f}%) from real APIs")
        print(f"   After: {new_total_real}/{total_points} points ({new_total_real/total_points*100:.0f}%) from real APIs")
        print(f"   Improvement: +{new_real_points} points (+{new_real_points/total_points*100:.0f}%)")
        
        print("\n" + "="*80)
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
