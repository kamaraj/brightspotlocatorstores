"""
Comprehensive 66-Point Data Collection Test
Demonstrates all enhanced data collectors
"""

import asyncio
import json
from datetime import datetime

# Import enhanced collectors
from app.core.data_collectors.demographics import DemographicsCollector
from app.core.data_collectors.competition_enhanced import CompetitionCollectorEnhanced
from app.core.data_collectors.accessibility_enhanced import AccessibilityCollectorEnhanced
from app.core.data_collectors.safety_enhanced import SafetyCollectorEnhanced
from app.core.data_collectors.economic_enhanced import EconomicCollectorEnhanced
from app.core.data_collectors.regulatory import RegulatoryCollector


async def collect_comprehensive_data(address: str) -> dict:
    """
    Collect all 66 data points from 6 enhanced collectors
    
    Returns:
        Dictionary with comprehensive analysis across all categories
    """
    
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE 66-POINT LOCATION ANALYSIS")
    print(f"{'='*80}")
    print(f"Address: {address}")
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Initialize collectors
    demographics = DemographicsCollector()
    competition = CompetitionCollectorEnhanced()
    accessibility = AccessibilityCollectorEnhanced()
    safety = SafetyCollectorEnhanced()
    economic = EconomicCollectorEnhanced()
    regulatory = RegulatoryCollector()
    
    # Collect all data
    print("📊 Collecting Demographics Data (15 points)...")
    demographics_data = await demographics.collect(address, radius_miles=2.0)
    print(f"   ✓ Demographics: {demographics_data.get('data_source', 'N/A')}")
    
    print("\n🏢 Collecting Competition Data (12 points)...")
    competition_data = await competition.collect(address, radius_miles=2.0)
    print(f"   ✓ Competition: {competition_data.get('data_source', 'N/A')}")
    
    print("\n🚗 Collecting Accessibility Data (10 points)...")
    accessibility_data = await accessibility.collect(address, radius_miles=5.0)
    print(f"   ✓ Accessibility: {accessibility_data.get('data_source', 'N/A')}")
    
    print("\n🛡️  Collecting Safety & Environment Data (11 points)...")
    safety_data = await safety.collect(address, radius_miles=1.0)
    print(f"   ✓ Safety: {safety_data.get('data_source', 'N/A')}")
    
    print("\n💰 Collecting Economic Data (10 points)...")
    economic_data = await economic.collect(address, radius_miles=2.0)
    print(f"   ✓ Economic: {economic_data.get('data_source', 'N/A')}")
    
    print("\n📋 Collecting Regulatory & Zoning Data (8 points)...")
    regulatory_data = await regulatory.collect(address, radius_miles=1.0)
    print(f"   ✓ Regulatory: {regulatory_data.get('data_source', 'N/A')}")
    
    # Compile comprehensive results
    comprehensive_results = {
        "address": address,
        "analysis_timestamp": datetime.now().isoformat(),
        "total_data_points": 66,
        
        "demographics": {
            "category_weight": 90,
            "data_points": 15,
            "data": demographics_data
        },
        
        "competition": {
            "category_weight": 75,
            "data_points": 12,
            "data": competition_data
        },
        
        "accessibility": {
            "category_weight": 65,
            "data_points": 10,
            "data": accessibility_data
        },
        
        "safety_environment": {
            "category_weight": 70,
            "data_points": 11,
            "data": safety_data
        },
        
        "economic_viability": {
            "category_weight": 55,
            "data_points": 10,
            "data": economic_data
        },
        
        "regulatory_zoning": {
            "category_weight": 50,
            "data_points": 8,
            "data": regulatory_data
        }
    }
    
    return comprehensive_results


def print_category_summary(category_name: str, data: dict, data_points_count: int):
    """Print summary for one category"""
    print(f"\n{'─'*80}")
    print(f"📌 {category_name.upper()} ({data_points_count} Data Points)")
    print(f"{'─'*80}")
    
    # Print up to 10 key metrics
    count = 0
    for key, value in data.items():
        if count >= 10:
            print(f"   ... and {data_points_count - count} more metrics")
            break
        
        if key not in ["success", "address", "coordinates", "data_source", "note", 
                       "jurisdiction", "state", "centers_details", "radius_miles",
                       "search_radius_miles", "centers_analyzed"]:
            
            # Format value
            if isinstance(value, bool):
                formatted_value = "Yes" if value else "No"
            elif isinstance(value, (int, float)):
                if value > 1000:
                    formatted_value = f"{value:,.0f}"
                else:
                    formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            
            # Format key (convert snake_case to Title Case)
            formatted_key = key.replace('_', ' ').title()
            
            print(f"   • {formatted_key}: {formatted_value}")
            count += 1


def calculate_category_scores(results: dict) -> dict:
    """
    Calculate overall category scores (0-100 scale)
    """
    scores = {}
    
    # Demographics score
    demo = results["demographics"]["data"]
    if demo.get("success", True):
        demo_score = (
            min(100, demo.get("population_density", 0) / 10) * 0.25 +
            min(100, demo.get("median_household_income", 0) / 1000) * 0.25 +
            min(100, demo.get("dual_income_rate", 0)) * 0.25 +
            min(100, demo.get("family_household_rate", 0)) * 0.25
        )
        scores["demographics"] = round(demo_score, 1)
    
    # Competition score (inverse - lower competition = higher score)
    comp = results["competition"]["data"]
    if comp.get("success", True):
        comp_score = (
            (100 - min(100, comp.get("market_saturation_index", 0) * 20)) * 0.4 +
            comp.get("market_gap_score", 50) * 0.3 +
            (100 - min(100, comp.get("competitive_intensity_score", 0))) * 0.3
        )
        scores["competition"] = round(comp_score, 1)
    
    # Accessibility score
    acc = results["accessibility"]["data"]
    if acc.get("success", True):
        acc_score = (
            acc.get("transit_score", 50) * 0.3 +
            acc.get("morning_rush_score", 50) * 0.3 +
            acc.get("parking_availability_score", 50) * 0.2 +
            acc.get("highway_visibility_score", 50) * 0.2
        )
        scores["accessibility"] = round(acc_score, 1)
    
    # Safety score (inverse for crime, direct for safety)
    safe = results["safety_environment"]["data"]
    if safe.get("success", True):
        safe_score = (
            (100 - safe.get("crime_rate_index", 30)) * 0.3 +
            safe.get("pedestrian_safety_score", 70) * 0.2 +
            (100 - min(100, safe.get("air_quality_index", 50) / 2)) * 0.2 +
            safe.get("neighborhood_safety_perception", 60) * 0.3
        )
        scores["safety_environment"] = round(safe_score, 1)
    
    # Economic score (normalize costs)
    econ = results["economic_viability"]["data"]
    if econ.get("success", True):
        econ_score = (
            (100 - min(100, econ.get("real_estate_cost_per_sqft", 150) / 4)) * 0.3 +
            econ.get("childcare_worker_availability_score", 60) * 0.3 +
            econ.get("business_incentives_score", 50) * 0.2 +
            econ.get("economic_growth_indicator", 55) * 0.2
        )
        scores["economic_viability"] = round(econ_score, 1)
    
    # Regulatory score
    reg = results["regulatory_zoning"]["data"]
    if reg.get("success", True):
        reg_score = (
            reg.get("zoning_compliance_score", 60) * 0.4 +
            reg.get("rezoning_feasibility_score", 65) * 0.2 +
            (100 - min(100, reg.get("building_code_complexity_score", 55))) * 0.2 +
            (100 - min(100, reg.get("licensing_difficulty_score", 55))) * 0.2
        )
        scores["regulatory_zoning"] = round(reg_score, 1)
    
    # Overall weighted score
    total_weight = sum([
        results["demographics"]["category_weight"],
        results["competition"]["category_weight"],
        results["accessibility"]["category_weight"],
        results["safety_environment"]["category_weight"],
        results["economic_viability"]["category_weight"],
        results["regulatory_zoning"]["category_weight"]
    ])
    
    weighted_sum = (
        scores.get("demographics", 0) * results["demographics"]["category_weight"] +
        scores.get("competition", 0) * results["competition"]["category_weight"] +
        scores.get("accessibility", 0) * results["accessibility"]["category_weight"] +
        scores.get("safety_environment", 0) * results["safety_environment"]["category_weight"] +
        scores.get("economic_viability", 0) * results["economic_viability"]["category_weight"] +
        scores.get("regulatory_zoning", 0) * results["regulatory_zoning"]["category_weight"]
    )
    
    scores["overall"] = round(weighted_sum / total_weight, 1)
    
    return scores


async def main():
    """
    Main test function - demonstrates comprehensive 66-point analysis
    """
    
    # Test addresses
    test_addresses = [
        "1600 Amphitheatre Parkway, Mountain View, CA 94043",  # Google HQ
        "1 Microsoft Way, Redmond, WA 98052",                  # Microsoft HQ
        "410 Terry Avenue North, Seattle, WA 98109"            # Amazon HQ
    ]
    
    print("\n" + "="*80)
    print("COMPREHENSIVE 66-POINT CHILDCARE LOCATION INTELLIGENCE SYSTEM")
    print("="*80)
    print("\nThis test demonstrates all 6 enhanced data collectors:")
    print("  1. Demographics (15 data points)")
    print("  2. Competition (12 data points)")
    print("  3. Accessibility (10 data points)")
    print("  4. Safety & Environment (11 data points)")
    print("  5. Economic Viability (10 data points)")
    print("  6. Regulatory & Zoning (8 data points)")
    print("\nTotal: 66 data points across 6 categories")
    print("="*80)
    
    # Analyze first address
    address = test_addresses[0]
    
    try:
        # Collect all data
        results = await collect_comprehensive_data(address)
        
        # Print category summaries
        print("\n\n" + "="*80)
        print("ANALYSIS RESULTS")
        print("="*80)
        
        print_category_summary(
            "Demographics",
            results["demographics"]["data"],
            results["demographics"]["data_points"]
        )
        
        print_category_summary(
            "Competition",
            results["competition"]["data"],
            results["competition"]["data_points"]
        )
        
        print_category_summary(
            "Accessibility",
            results["accessibility"]["data"],
            results["accessibility"]["data_points"]
        )
        
        print_category_summary(
            "Safety & Environment",
            results["safety_environment"]["data"],
            results["safety_environment"]["data_points"]
        )
        
        print_category_summary(
            "Economic Viability",
            results["economic_viability"]["data"],
            results["economic_viability"]["data_points"]
        )
        
        print_category_summary(
            "Regulatory & Zoning",
            results["regulatory_zoning"]["data"],
            results["regulatory_zoning"]["data_points"]
        )
        
        # Calculate and display scores
        scores = calculate_category_scores(results)
        
        print(f"\n\n{'='*80}")
        print("CATEGORY SCORES (0-100 scale)")
        print(f"{'='*80}")
        print(f"   Demographics:        {scores.get('demographics', 0):.1f}/100")
        print(f"   Competition:         {scores.get('competition', 0):.1f}/100")
        print(f"   Accessibility:       {scores.get('accessibility', 0):.1f}/100")
        print(f"   Safety & Environment: {scores.get('safety_environment', 0):.1f}/100")
        print(f"   Economic Viability:  {scores.get('economic_viability', 0):.1f}/100")
        print(f"   Regulatory & Zoning: {scores.get('regulatory_zoning', 0):.1f}/100")
        print(f"{'─'*80}")
        print(f"   OVERALL SCORE:       {scores.get('overall', 0):.1f}/100")
        print(f"{'='*80}\n")
        
        # Save to JSON
        output_file = f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Full analysis saved to: {output_file}")
        
        # Recommendation
        overall_score = scores.get('overall', 0)
        if overall_score >= 75:
            recommendation = "EXCELLENT - Highly recommended location"
        elif overall_score >= 60:
            recommendation = "GOOD - Suitable location with minor considerations"
        elif overall_score >= 45:
            recommendation = "FAIR - Consider improvements or alternative locations"
        else:
            recommendation = "POOR - Not recommended without significant changes"
        
        print(f"\n📊 RECOMMENDATION: {recommendation}")
        print(f"\n{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive 66-point analysis...")
    asyncio.run(main())
