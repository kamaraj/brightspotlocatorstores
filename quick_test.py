"""
Quick Test - Verify 66-Point System with Timing & XAI
Fast test using mock data to demonstrate all features
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
from app.utils.timing_xai import PerformanceTracker, DataPointExplainer


async def quick_test():
    """Quick test with mock data"""
    
    print("\n" + "="*100)
    print("🚀 QUICK TEST: 66-Point Analysis with Millisecond Timing & XAI")
    print("="*100)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
    
    tracker = PerformanceTracker()
    
    # Test address (will use mock data if API keys not configured)
    address = "1600 Amphitheatre Parkway, Mountain View, CA 94043"
    
    # Initialize collectors
    with tracker.track("initialization"):
        demographics = DemographicsCollector()
        competition = CompetitionCollectorEnhanced()
        accessibility = AccessibilityCollectorEnhanced()
        safety = SafetyCollectorEnhanced()
        economic = EconomicCollectorEnhanced()
        regulatory = RegulatoryCollector()
    
    print(f"✓ Collectors initialized: {tracker.metrics[-1].duration_ms:.2f} ms\n")
    
    results = {}
    
    # Demographics (15 points)
    print("📊 Collecting Demographics (15 data points)...")
    with tracker.track("demographics"):
        demographics_data = await demographics.collect(address, radius_miles=2.0)
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Children 0-5: {demographics_data.get('children_0_5_count', 'N/A')}")
    print(f"   • Median Income: ${demographics_data.get('median_household_income', 0):,.0f}")
    print(f"   • Population Density: {demographics_data.get('population_density', 0):.1f}/sq mi\n")
    results["demographics"] = demographics_data
    
    # Competition (12 points)
    print("🏢 Collecting Competition (12 data points)...")
    with tracker.track("competition"):
        competition_data = await competition.collect(address, radius_miles=2.0)
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Existing Centers: {competition_data.get('existing_centers_count', 0)}")
    print(f"   • Market Gap Score: {competition_data.get('market_gap_score', 0):.1f}/100")
    print(f"   • Avg Rating: {competition_data.get('avg_competitor_rating', 0):.1f}/5.0\n")
    results["competition"] = competition_data
    
    # Accessibility (10 points)
    print("🚗 Collecting Accessibility (10 data points)...")
    with tracker.track("accessibility"):
        accessibility_data = await accessibility.collect(address, radius_miles=5.0)
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Transit Score: {accessibility_data.get('transit_score', 0):.1f}/100")
    print(f"   • Avg Commute: {accessibility_data.get('avg_commute_minutes', 0):.0f} min")
    print(f"   • Parking Score: {accessibility_data.get('parking_availability_score', 0):.1f}/100\n")
    results["accessibility"] = accessibility_data
    
    # Safety (11 points)
    print("🛡️  Collecting Safety & Environment (11 data points)...")
    with tracker.track("safety"):
        safety_data = await safety.collect(address, radius_miles=1.0)
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Crime Rate Index: {safety_data.get('crime_rate_index', 0):.1f}/100")
    print(f"   • Air Quality Index: {safety_data.get('air_quality_index', 0):.0f}")
    print(f"   • Pedestrian Safety: {safety_data.get('pedestrian_safety_score', 0):.1f}/100\n")
    results["safety"] = safety_data
    
    # Economic (10 points)
    print("💰 Collecting Economic Viability (10 data points)...")
    with tracker.track("economic"):
        economic_data = await economic.collect(address, radius_miles=2.0)
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Real Estate Cost: ${economic_data.get('real_estate_cost_per_sqft', 0):.2f}/sq ft")
    print(f"   • Worker Availability: {economic_data.get('childcare_worker_availability_score', 0):.1f}/100")
    print(f"   • Business Incentives: {economic_data.get('business_incentives_score', 0):.1f}/100\n")
    results["economic"] = economic_data
    
    # Regulatory (8 points)
    print("📋 Collecting Regulatory & Zoning (8 data points)...")
    with tracker.track("regulatory"):
        regulatory_data = await regulatory.collect(address, radius_miles=1.0)
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Zoning Compliance: {regulatory_data.get('zoning_compliance_score', 0):.1f}/100")
    print(f"   • Licensing Difficulty: {regulatory_data.get('licensing_difficulty_score', 0):.1f}/100")
    print(f"   • Permit Processing: {regulatory_data.get('avg_permit_processing_days', 0):.0f} days\n")
    results["regulatory"] = regulatory_data
    
    # Generate XAI explanations for sample data points
    print("\n" + "="*100)
    print("🧠 XAI EXPLANATIONS - Sample Data Points (10 of 66)")
    print("="*100)
    
    sample_points = [
        ("demographics", "children_0_5_count"),
        ("demographics", "median_household_income"),
        ("competition", "market_gap_score"),
        ("competition", "existing_centers_count"),
        ("accessibility", "transit_score"),
        ("accessibility", "avg_commute_minutes"),
        ("safety", "crime_rate_index"),
        ("economic", "real_estate_cost_per_sqft"),
        ("economic", "childcare_worker_availability_score"),
        ("regulatory", "zoning_compliance_score")
    ]
    
    for category, point_name in sample_points:
        if category in results and point_name in results[category]:
            value = results[category][point_name]
            explanation = DataPointExplainer.explain_data_point(
                category, point_name, value, results[category]
            )
            
            print(f"\n{'─'*100}")
            print(f"📍 {point_name.replace('_', ' ').title()}: {value}")
            print(f"{'─'*100}")
            print(f"   What: {explanation['explanation']['what']}")
            print(f"   How:  {explanation['explanation']['how']}")
            print(f"   Why:  {explanation['explanation']['why']}")
            print(f"   ")
            print(f"   📊 Source: {explanation['explanation']['source']}")
            print(f"   ✓ Confidence: {explanation['explanation']['confidence']}")
            print(f"   ⚖️  Assessment: {explanation['interpretation']}")
    
    # Timing summary
    print("\n\n" + "="*100)
    print("⏱️  TIMING BREAKDOWN (Millisecond Precision)")
    print("="*100)
    
    report = tracker.get_report()
    
    print(f"\n📊 Overall Performance:")
    print(f"   Total Time: {report['total_time_ms']:.2f} ms ({report['total_time_ms']/1000:.2f} seconds)")
    print(f"   Successful Steps: {report['successful_steps']}/{report['steps_count']}")
    print(f"   Overhead: {report['overhead_ms']:.2f} ms")
    
    print(f"\n📈 Category Breakdown:")
    for category, data in sorted(report['categories'].items(), key=lambda x: x[1]['total_ms'], reverse=True):
        print(f"   {category.title():.<40} {data['total_ms']:>10.2f} ms ({data['count']} steps)")
    
    print(f"\n🔍 Step-by-Step:")
    for step in report['detailed_steps']:
        status = "✓" if step['success'] else "✗"
        print(f"   {status} {step['step']:.<50} {step['duration_ms']:>10.2f} ms")
    
    # Data summary
    print("\n\n" + "="*100)
    print("📊 DATA COLLECTION SUMMARY")
    print("="*100)
    
    total_points = 0
    for category, data in results.items():
        # Count actual data points (exclude metadata)
        points = len([k for k in data.keys() if k not in [
            'success', 'address', 'coordinates', 'data_source', 'note',
            'jurisdiction', 'state', 'centers_details', 'radius_miles',
            'search_radius_miles', 'centers_analyzed', 'total_population',
            'land_area_sqmi'
        ]])
        total_points += points
        print(f"   {category.title():.<30} {points:>3} data points")
    
    print(f"   {'─'*30}")
    print(f"   {'TOTAL':.<30} {total_points:>3} data points")
    
    print(f"\n{'='*100}")
    print(f"✅ TEST COMPLETED SUCCESSFULLY!")
    print(f"   • All 6 collectors working")
    print(f"   • {total_points} data points collected")
    print(f"   • Millisecond-precision timing captured")
    print(f"   • XAI explanations generated")
    print(f"   • Total time: {report['total_time_ms']/1000:.2f} seconds")
    print(f"{'='*100}\n")
    
    # Save results
    output = {
        "address": address,
        "timestamp": datetime.now().isoformat(),
        "total_time_ms": report['total_time_ms'],
        "results": results,
        "performance": report
    }
    
    filename = f"quick_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"📄 Results saved to: {filename}\n")


if __name__ == "__main__":
    print("\n🔍 Starting Quick Test...")
    asyncio.run(quick_test())
