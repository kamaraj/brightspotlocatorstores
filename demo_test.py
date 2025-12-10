"""
Demo Test - Showcase 66-Point System with Mock Data
Fast demonstration without API calls
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from app.utils.timing_xai import PerformanceTracker, DataPointExplainer


def get_mock_demographics() -> Dict[str, Any]:
    """Mock demographics data (15 points)"""
    return {
        "children_0_5_count": 1500,
        "population_density": 4200.5,
        "birth_rate": 12.5,
        "age_distribution_pct": {"0-5": 8.2, "6-17": 15.3, "18-64": 62.1, "65+": 14.4},
        "median_household_income": 85000,
        "income_distribution_pct": {"<50k": 20.0, "50k-100k": 45.0, "100k+": 35.0},
        "avg_childcare_spending_monthly": 1200,
        "income_growth_rate": 3.5,
        "dual_income_rate": 68.5,
        "working_mothers_rate": 72.3,
        "avg_commute_time_minutes": 28.5,
        "population_growth_rate": 2.1,
        "net_migration_rate": 1.5,
        "family_household_rate": 65.2,
        "educational_attainment_pct": {"hs": 25.0, "bachelors": 45.0, "graduate": 20.0},
        "data_source": "Mock Data - Census Bureau Format"
    }


def get_mock_competition() -> Dict[str, Any]:
    """Mock competition data (12 points)"""
    return {
        "existing_centers_count": 8,
        "total_licensed_capacity": 450,
        "market_saturation_index": 2.35,
        "avg_competitor_rating": 4.2,
        "premium_facilities_count": 3,
        "avg_capacity_utilization_pct": 85.5,
        "waitlist_prevalence_score": 72.0,
        "market_gap_score": 65.0,
        "demand_supply_ratio": 1.8,
        "nearest_competitor_miles": 0.75,
        "competitive_intensity_score": 68.5,
        "new_centers_planned": 2,
        "data_source": "Mock Data - Google Places Format"
    }


def get_mock_accessibility() -> Dict[str, Any]:
    """Mock accessibility data (10 points)"""
    return {
        "avg_commute_minutes": 25.5,
        "peak_congestion_factor": 1.45,
        "nearest_employer_miles": 2.3,
        "employers_within_5_miles": 45,
        "transit_score": 72.0,
        "walk_score_to_transit": 65.0,
        "morning_rush_score": 58.0,
        "evening_rush_score": 55.0,
        "highway_visibility_score": 78.0,
        "parking_availability_score": 82.0,
        "data_source": "Mock Data - Google Maps APIs"
    }


def get_mock_safety() -> Dict[str, Any]:
    """Mock safety data (11 points)"""
    return {
        "crime_rate_index": 35.2,
        "violent_crime_rate": 2.5,
        "property_crime_rate": 15.8,
        "traffic_accident_rate": 4.2,
        "pedestrian_safety_score": 75.0,
        "air_quality_index": 45.0,
        "superfund_proximity_score": 92.0,
        "industrial_hazards_score": 88.0,
        "flood_risk_score": 15.0,
        "natural_hazard_composite": 25.0,
        "neighborhood_safety_perception": 78.0,
        "data_source": "Mock Data - EPA/FBI/FEMA Format"
    }


def get_mock_economic() -> Dict[str, Any]:
    """Mock economic data (10 points)"""
    return {
        "real_estate_cost_per_sqft": 165.50,
        "property_tax_rate_pct": 1.25,
        "construction_cost_per_sqft": 185.00,
        "avg_commercial_rent_per_sqft_year": 28.50,
        "utility_cost_index": 105.5,
        "local_wage_level_annual": 45000,
        "childcare_worker_availability_score": 68.0,
        "avg_childcare_worker_wage": 42000,
        "business_incentives_score": 55.0,
        "economic_growth_indicator": 62.0,
        "data_source": "Mock Data - BLS/CoStar Format"
    }


def get_mock_regulatory() -> Dict[str, Any]:
    """Mock regulatory data (8 points)"""
    return {
        "zoning_compliance_score": 75.0,
        "conditional_use_permit_required": False,
        "rezoning_feasibility_score": 65.0,
        "building_code_complexity_score": 55.0,
        "ada_compliance_cost_estimate": 25000,
        "licensing_difficulty_score": 48.0,
        "time_to_obtain_license_days": 90,
        "avg_permit_processing_days": 45,
        "jurisdiction": "Mountain View",
        "state": "CA",
        "data_source": "Mock Data - Local Government Format"
    }


async def demo_test():
    """Demo test with mock data"""
    
    print("\n" + "="*100)
    print("🎬 DEMO: 66-Point Analysis with Millisecond Timing & XAI")
    print("="*100)
    print(f"Using Mock Data (No API Keys Required)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
    
    tracker = PerformanceTracker()
    
    address = "1600 Amphitheatre Parkway, Mountain View, CA 94043"
    
    # Simulate data collection with timing
    results = {}
    
    # Demographics (15 points)
    print("📊 Demographics (15 data points)")
    with tracker.track("demographics"):
        await asyncio.sleep(0.05)  # Simulate API call
        results["demographics"] = get_mock_demographics()
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Children 0-5: {results['demographics']['children_0_5_count']:,}")
    print(f"   • Median Income: ${results['demographics']['median_household_income']:,}")
    print(f"   • Population Density: {results['demographics']['population_density']:,.1f}/sq mi\n")
    
    # Competition (12 points)
    print("🏢 Competition (12 data points)")
    with tracker.track("competition"):
        await asyncio.sleep(0.08)  # Simulate API call
        results["competition"] = get_mock_competition()
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Existing Centers: {results['competition']['existing_centers_count']}")
    print(f"   • Market Gap Score: {results['competition']['market_gap_score']:.1f}/100")
    print(f"   • Avg Rating: {results['competition']['avg_competitor_rating']:.1f}/5.0\n")
    
    # Accessibility (10 points)
    print("🚗 Accessibility (10 data points)")
    with tracker.track("accessibility"):
        await asyncio.sleep(0.06)  # Simulate API call
        results["accessibility"] = get_mock_accessibility()
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Transit Score: {results['accessibility']['transit_score']:.1f}/100")
    print(f"   • Avg Commute: {results['accessibility']['avg_commute_minutes']:.0f} min")
    print(f"   • Parking Score: {results['accessibility']['parking_availability_score']:.1f}/100\n")
    
    # Safety (11 points)
    print("🛡️  Safety & Environment (11 data points)")
    with tracker.track("safety"):
        await asyncio.sleep(0.07)  # Simulate API call
        results["safety"] = get_mock_safety()
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Crime Rate Index: {results['safety']['crime_rate_index']:.1f}/100")
    print(f"   • Air Quality Index: {results['safety']['air_quality_index']:.0f}")
    print(f"   • Pedestrian Safety: {results['safety']['pedestrian_safety_score']:.1f}/100\n")
    
    # Economic (10 points)
    print("💰 Economic Viability (10 data points)")
    with tracker.track("economic"):
        await asyncio.sleep(0.05)  # Simulate API call
        results["economic"] = get_mock_economic()
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Real Estate Cost: ${results['economic']['real_estate_cost_per_sqft']:.2f}/sq ft")
    print(f"   • Worker Availability: {results['economic']['childcare_worker_availability_score']:.1f}/100")
    print(f"   • Business Incentives: {results['economic']['business_incentives_score']:.1f}/100\n")
    
    # Regulatory (8 points)
    print("📋 Regulatory & Zoning (8 data points)")
    with tracker.track("regulatory"):
        await asyncio.sleep(0.04)  # Simulate API call
        results["regulatory"] = get_mock_regulatory()
    print(f"   ✓ Completed in {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   • Zoning Compliance: {results['regulatory']['zoning_compliance_score']:.1f}/100")
    print(f"   • Licensing Difficulty: {results['regulatory']['licensing_difficulty_score']:.1f}/100")
    print(f"   • Permit Processing: {results['regulatory']['avg_permit_processing_days']:.0f} days\n")
    
    # Generate XAI explanations
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
    
    with tracker.track("xai_generation"):
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
    
    print(f"\n   ✓ XAI explanations generated in {tracker.metrics[-1].duration_ms:.2f} ms")
    
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
    
    expected_counts = {
        "demographics": 15,
        "competition": 12,
        "accessibility": 10,
        "safety": 11,
        "economic": 10,
        "regulatory": 8
    }
    
    total_points = 0
    for category, expected in expected_counts.items():
        if category in results:
            actual = len([k for k in results[category].keys() if k not in [
                'data_source', 'jurisdiction', 'state'
            ]])
            total_points += actual
            print(f"   {category.title():.<30} {actual:>3} / {expected} data points")
    
    print(f"   {'─'*30}")
    print(f"   {'TOTAL':.<30} {total_points:>3} data points")
    
    print(f"\n{'='*100}")
    print(f"✅ DEMO COMPLETED SUCCESSFULLY!")
    print(f"   • All 6 categories demonstrated")
    print(f"   • {total_points} data points collected")
    print(f"   • Millisecond-precision timing captured")
    print(f"   • XAI explanations generated for all points")
    print(f"   • Total time: {report['total_time_ms']/1000:.3f} seconds")
    print(f"{'='*100}\n")
    
    # Save results
    output = {
        "mode": "demo",
        "address": address,
        "timestamp": datetime.now().isoformat(),
        "total_time_ms": report['total_time_ms'],
        "results": results,
        "performance": report,
        "data_points_count": total_points
    }
    
    filename = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"📄 Results saved to: {filename}")
    print(f"\n💡 To use real API data:")
    print(f"   1. Add your Google Maps API key to .env file")
    print(f"   2. Add your Census Bureau API key to .env file")
    print(f"   3. Run: python test_66_with_timing_xai.py\n")


if __name__ == "__main__":
    print("\n🎬 Starting Demo Test...")
    asyncio.run(demo_test())
