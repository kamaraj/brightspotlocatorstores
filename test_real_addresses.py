"""
Comprehensive Real Address Testing
Tests the production system with actual locations across different scenarios
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any


# Test locations with different characteristics
TEST_LOCATIONS = [
    {
        "name": "Affluent Suburban (North Lauderdale, FL)",
        "address": "North Lauderdale, FL 33068",
        "expected": "Good demographics, moderate competition"
    },
    {
        "name": "Tech Hub (Mountain View, CA - Google HQ)",
        "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        "expected": "High income, high competition, high costs"
    },
    {
        "name": "Urban Dense (New York, NY - Manhattan)",
        "address": "Times Square, New York, NY 10036",
        "expected": "High density, very high competition, premium pricing"
    },
    {
        "name": "Growing Suburban (Austin, TX)",
        "address": "Austin, TX 78701",
        "expected": "Growing market, moderate competition"
    },
    {
        "name": "Rural Area (Small Town)",
        "address": "Lexington, VA 24450",
        "expected": "Low competition, smaller market"
    }
]


async def analyze_location(address: str, radius: float = 2.0) -> Dict[str, Any]:
    """Send analysis request to production server"""
    url = "http://127.0.0.1:9025/api/v1/analyze"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url,
                json={"address": address, "radius_miles": radius},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {"error": f"Status {response.status}: {error_text}"}
        except Exception as e:
            return {"error": str(e)}


def print_results(location_name: str, address: str, result: Dict[str, Any]):
    """Print formatted analysis results"""
    print("\n" + "="*80)
    print(f"📍 {location_name}")
    print("="*80)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n🏠 Original Address: {result.get('original_address', address)}")
    
    # Address validation
    if result.get('address_validation', {}).get('corrected'):
        print(f"✅ Corrected To: {result.get('address', 'N/A')}")
        components = result.get('address_validation', {}).get('components', {})
        print(f"   City: {components.get('city', 'N/A')}")
        print(f"   State: {components.get('state', 'N/A')}")
        print(f"   ZIP: {components.get('zip_code', 'N/A')}")
    
    # Overall score
    score = result.get('overall_score', 0)
    recommendation = result.get('recommendation', 'N/A')
    print(f"\n🎯 Overall Score: {score}/100")
    print(f"💡 Recommendation: {recommendation}")
    
    # Category scores
    print(f"\n📊 Category Breakdown:")
    categories = result.get('categories', {})
    
    for category, data in categories.items():
        cat_score = data.get('score', 0)
        
        # Visual bar
        bar_length = int(cat_score / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        print(f"   {category.ljust(15)}: {bar} {cat_score:.1f}/100")
    
    # Key insights
    insights = result.get('key_insights', [])
    if insights:
        print(f"\n🔍 Key Insights:")
        for insight in insights[:5]:  # Show top 5
            print(f"   • {insight}")
    
    # Timing
    timing = result.get('timing', {})
    total_time = result.get('analysis_time_ms', 0)
    print(f"\n⏱️  Analysis Time: {total_time:.0f}ms")
    print(f"   Demographics: {timing.get('demographics_ms', 0):.0f}ms")
    print(f"   Competition: {timing.get('competition_ms', 0):.0f}ms")
    print(f"   Accessibility: {timing.get('accessibility_ms', 0):.0f}ms")
    print(f"   Environmental: {timing.get('environmental_ms', 0):.0f}ms")
    print(f"   Crime: {timing.get('crime_ms', 0):.0f}ms")
    print(f"   Flood: {timing.get('flood_ms', 0):.0f}ms")
    print(f"   Safety: {timing.get('safety_ms', 0):.0f}ms")
    print(f"   Housing: {timing.get('housing_ms', 0):.0f}ms")
    print(f"   Economic: {timing.get('economic_ms', 0):.0f}ms")
    print(f"   Regulatory: {timing.get('regulatory_ms', 0):.0f}ms")
    
    # Data points
    data_points = result.get('data_points_collected', 66)
    print(f"\n📈 Data Points Collected: {data_points}")
    
    # Sample some interesting metrics
    print(f"\n📊 Sample Metrics:")
    demo = categories.get('demographics', {}).get('data', {})
    comp = categories.get('competition', {}).get('data', {})
    safety = categories.get('safety', {}).get('data', {})
    econ = categories.get('economic', {}).get('data', {})
    
    if demo:
        print(f"   Children (0-5): {demo.get('children_0_5_count', 0):,}")
        print(f"   Median Income: ${demo.get('median_household_income', 0):,}")
        print(f"   Dual Income: {demo.get('dual_income_rate', 0):.1f}%")
    
    if comp:
        print(f"   Existing Centers: {comp.get('existing_centers_count', 0)}")
        print(f"   Market Saturation: {comp.get('market_saturation_index', 0):.2f}")
    
    if safety:
        print(f"   Crime Index: {safety.get('crime_rate_index', 0):.1f}/100")
        print(f"   Air Quality: {safety.get('air_quality_index', 0):.1f}")
        if 'flood_zone' in safety:
            print(f"   Flood Zone: {safety.get('flood_zone', 'N/A')}")
    
    if econ:
        print(f"   Real Estate Cost: ${econ.get('real_estate_cost_per_sqft', 0):.2f}/sqft")
        print(f"   Startup Cost: ${econ.get('startup_cost_estimate', 0):,.0f}")


async def test_all_locations():
    """Test all predefined locations"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE LOCATION TESTING")
    print("="*80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Server: http://127.0.0.1:9025/")
    print(f"📍 Testing {len(TEST_LOCATIONS)} locations")
    
    results = []
    
    for location in TEST_LOCATIONS:
        print(f"\n⏳ Analyzing: {location['name']}...")
        
        result = await analyze_location(location['address'])
        results.append({
            'location': location,
            'result': result
        })
        
        print_results(location['name'], location['address'], result)
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if 'error' not in r['result'])
    failed = len(results) - successful
    
    print(f"\n✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    if successful > 0:
        # Calculate average scores
        scores = [r['result'].get('overall_score', 0) for r in results if 'error' not in r['result']]
        avg_score = sum(scores) / len(scores)
        
        print(f"\n📈 Average Overall Score: {avg_score:.1f}/100")
        print(f"   Highest: {max(scores):.1f}")
        print(f"   Lowest: {min(scores):.1f}")
        
        # Average analysis time
        times = [r['result'].get('analysis_time_ms', 0) for r in results if 'error' not in r['result']]
        avg_time = sum(times) / len(times)
        
        print(f"\n⏱️  Average Analysis Time: {avg_time:.0f}ms")
        print(f"   Fastest: {min(times):.0f}ms")
        print(f"   Slowest: {max(times):.0f}ms")
    
    print("\n" + "="*80)
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Save results to file
    output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")


async def test_custom_address(address: str):
    """Test a single custom address"""
    print("\n" + "="*80)
    print("🧪 CUSTOM ADDRESS TEST")
    print("="*80)
    
    result = await analyze_location(address)
    print_results("Custom Location", address, result)


async def main():
    """Main test runner"""
    import sys
    
    if len(sys.argv) > 1:
        # Test custom address from command line
        custom_address = " ".join(sys.argv[1:])
        await test_custom_address(custom_address)
    else:
        # Test all predefined locations
        await test_all_locations()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
