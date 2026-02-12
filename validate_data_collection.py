"""
Comprehensive Data Validation Script
Tests all 6 category collectors and validates 66 data points
"""
import asyncio
import json
from datetime import datetime

from app.core.data_collectors.demographics import DemographicsCollector
from app.core.data_collectors.competition_enhanced import CompetitionCollectorEnhanced
from app.core.data_collectors.accessibility_enhanced import AccessibilityCollectorEnhanced
from app.core.data_collectors.safety_enhanced import SafetyCollectorEnhanced
from app.core.data_collectors.economic_enhanced import EconomicCollectorEnhanced
from app.core.data_collectors.regulatory import RegulatoryCollector


async def validate_data_collection():
    """Validate all data collectors"""
    
    # Test address
    test_address = "1600 Amphitheatre Parkway, Mountain View, CA 94043"
    
    print("="*80)
    print("DATA COLLECTION VALIDATION")
    print("="*80)
    print(f"Test Address: {test_address}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    results = {}
    
    # Test Demographics (15 data points)
    print("\n[1/6] Testing Demographics Collector (15 data points)...")
    demographics = DemographicsCollector()
    demo_data = await demographics.collect(test_address, radius_miles=2.0)
    results['demographics'] = demo_data
    
    if demo_data.get('success'):
        print("    Status: SUCCESS")
        print(f"    Data Source: {demo_data.get('data_source', 'Unknown')}")
        print(f"    Children 0-5: {demo_data.get('children_0_5_count', 0)}")
        print(f"    Median Income: ${demo_data.get('median_household_income', 0):,}")
    else:
        print(f"    Status: FAILED - {demo_data.get('error', 'Unknown error')}")
    
    # Test Competition (12 data points)
    print("\n[2/6] Testing Competition Collector (12 data points)...")
    competition = CompetitionCollectorEnhanced()
    comp_data = await competition.collect(test_address, radius_miles=2.0)
    results['competition'] = comp_data
    
    if comp_data.get('success'):
        print("    Status: SUCCESS")
        print(f"    Childcare Centers: {comp_data.get('childcare_centers_count', 0)}")
        print(f"    Market Gap Score: {comp_data.get('market_gap_score', 0)}")
    else:
        print(f"    Status: FAILED - {comp_data.get('error', 'Unknown error')}")
    
    # Test Accessibility (10 data points)
    print("\n[3/6] Testing Accessibility Collector (10 data points)...")
    accessibility = AccessibilityCollectorEnhanced()
    acc_data = await accessibility.collect(test_address, radius_miles=5.0)
    results['accessibility'] = acc_data
    
    if acc_data.get('success'):
        print("    Status: SUCCESS")
        print(f"    Transit Score: {acc_data.get('transit_score', 0)}")
        print(f"    Parking Score: {acc_data.get('parking_availability_score', 0)}")
    else:
        print(f"    Status: FAILED - {acc_data.get('error', 'Unknown error')}")
    
    # Test Safety (11 data points)
    print("\n[4/6] Testing Safety Collector (11 data points)...")
    safety = SafetyCollectorEnhanced()
    safety_data = await safety.collect(test_address, radius_miles=1.0)
    results['safety'] = safety_data
    
    if safety_data.get('success'):
        print("    Status: SUCCESS")
        print(f"    Crime Rate Index: {safety_data.get('crime_rate_index', 0)}")
        print(f"    Air Quality Index: {safety_data.get('air_quality_index', 0)}")
    else:
        print(f"    Status: FAILED - {safety_data.get('error', 'Unknown error')}")
    
    # Test Economic (10 data points)
    print("\n[5/6] Testing Economic Collector (10 data points)...")
    economic = EconomicCollectorEnhanced()
    econ_data = await economic.collect(test_address, radius_miles=2.0)
    results['economic'] = econ_data
    
    if econ_data.get('success'):
        print("    Status: SUCCESS")
        print(f"    Real Estate Cost: ${econ_data.get('real_estate_cost_per_sqft', 0)}/sqft")
        print(f"    Worker Availability: {econ_data.get('childcare_worker_availability_score', 0)}")
    else:
        print(f"    Status: FAILED - {econ_data.get('error', 'Unknown error')}")
    
    # Test Regulatory (8 data points)
    print("\n[6/6] Testing Regulatory Collector (8 data points)...")
    regulatory = RegulatoryCollector()
    reg_data = await regulatory.collect(test_address, radius_miles=1.0)
    results['regulatory'] = reg_data
    
    if reg_data.get('success'):
        print("    Status: SUCCESS")
        print(f"    Zoning Compliance: {reg_data.get('zoning_compliance_score', 0)}")
        print(f"    Licensing Difficulty: {reg_data.get('licensing_difficulty_score', 0)}")
    else:
        print(f"    Status: FAILED - {reg_data.get('error', 'Unknown error')}")
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    
    print(f"Categories Successful: {success_count}/{total_count}")
    
    for category, data in results.items():
        status = "PASS" if data.get('success') else "FAIL"
        source = data.get('data_source', 'Unknown')
        print(f"  {category.capitalize():15} [{status}] - {source}")
    
    # Check for real API data vs mock data
    print("\n" + "="*80)
    print("DATA SOURCE ANALYSIS")
    print("="*80)
    
    real_api_count = 0
    mock_data_count = 0
    
    for category, data in results.items():
        source = data.get('data_source', '')
        if 'Mock' in source or 'mock' in source:
            print(f"  {category.capitalize():15} - MOCK DATA")
            mock_data_count += 1
        elif data.get('success'):
            print(f"  {category.capitalize():15} - REAL API DATA")
            real_api_count += 1
        else:
            print(f"  {category.capitalize():15} - ERROR/NO DATA")
    
    print(f"\nReal API Data: {real_api_count}/{total_count}")
    print(f"Mock Data: {mock_data_count}/{total_count}")
    
    # Save results to file
    output_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Final verdict
    print("\n" + "="*80)
    if success_count == total_count and mock_data_count == 0:
        print("VALIDATION: PASSED - All categories using real API data")
    elif success_count == total_count:
        print(f"VALIDATION: PARTIAL - All categories working but {mock_data_count} using mock data")
    else:
        print(f"VALIDATION: FAILED - {total_count - success_count} categories failed")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(validate_data_collection())
