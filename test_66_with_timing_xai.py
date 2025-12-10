"""
Enhanced 66-Point Analysis with Timing and XAI
Shows millisecond-precision timing and explainable AI justifications
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import collectors
from app.core.data_collectors.demographics import DemographicsCollector
from app.core.data_collectors.competition_enhanced import CompetitionCollectorEnhanced
from app.core.data_collectors.accessibility_enhanced import AccessibilityCollectorEnhanced
from app.core.data_collectors.safety_enhanced import SafetyCollectorEnhanced
from app.core.data_collectors.economic_enhanced import EconomicCollectorEnhanced
from app.core.data_collectors.regulatory import RegulatoryCollector

# Import timing and XAI utilities
from app.utils.timing_xai import PerformanceTracker, DataPointExplainer


async def collect_with_timing_and_xai(address: str) -> Dict[str, Any]:
    """
    Collect all 66 data points with detailed timing and XAI explanations
    """
    
    print(f"\n{'='*100}")
    print(f"COMPREHENSIVE 66-POINT ANALYSIS WITH TIMING & XAI")
    print(f"{'='*100}")
    print(f"Address: {address}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    print(f"{'='*100}\n")
    
    # Create performance tracker
    tracker = PerformanceTracker()
    
    # Initialize collectors
    with tracker.track("initialization"):
        demographics = DemographicsCollector()
        competition = CompetitionCollectorEnhanced()
        accessibility = AccessibilityCollectorEnhanced()
        safety = SafetyCollectorEnhanced()
        economic = EconomicCollectorEnhanced()
        regulatory = RegulatoryCollector()
    
    print(f"✓ Collectors initialized: {tracker.metrics[-1].duration_ms:.2f} ms\n")
    
    # Collect data with timing for each category
    results = {}
    
    # 1. Demographics (15 points)
    print("📊 DEMOGRAPHICS (15 data points)")
    print("-" * 100)
    with tracker.track("demographics_total"):
        with tracker.track("demographics_geocoding"):
            # Geocoding happens inside collect()
            pass
        demographics_data = await demographics.collect(address, radius_miles=2.0)
        
    print(f"   Total time: {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   Data points collected: 15")
    print(f"   Source: {demographics_data.get('data_source', 'N/A')}\n")
    
    results["demographics"] = demographics_data
    
    # 2. Competition (12 points)
    print("🏢 COMPETITION (12 data points)")
    print("-" * 100)
    with tracker.track("competition_total"):
        competition_data = await competition.collect(address, radius_miles=2.0)
        
    print(f"   Total time: {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   Data points collected: 12")
    print(f"   Centers analyzed: {competition_data.get('centers_analyzed', 0)}")
    print(f"   Source: {competition_data.get('data_source', 'N/A')}\n")
    
    results["competition"] = competition_data
    
    # 3. Accessibility (10 points)
    print("🚗 ACCESSIBILITY (10 data points)")
    print("-" * 100)
    with tracker.track("accessibility_total"):
        accessibility_data = await accessibility.collect(address, radius_miles=5.0)
        
    print(f"   Total time: {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   Data points collected: 10")
    print(f"   Source: {accessibility_data.get('data_source', 'N/A')}\n")
    
    results["accessibility"] = accessibility_data
    
    # 4. Safety & Environment (11 points)
    print("🛡️  SAFETY & ENVIRONMENT (11 data points)")
    print("-" * 100)
    with tracker.track("safety_total"):
        safety_data = await safety.collect(address, radius_miles=1.0)
        
    print(f"   Total time: {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   Data points collected: 11")
    print(f"   Source: {safety_data.get('data_source', 'N/A')}\n")
    
    results["safety"] = safety_data
    
    # 5. Economic Viability (10 points)
    print("💰 ECONOMIC VIABILITY (10 data points)")
    print("-" * 100)
    with tracker.track("economic_total"):
        economic_data = await economic.collect(address, radius_miles=2.0)
        
    print(f"   Total time: {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   Data points collected: 10")
    print(f"   Source: {economic_data.get('data_source', 'N/A')}\n")
    
    results["economic"] = economic_data
    
    # 6. Regulatory & Zoning (8 points)
    print("📋 REGULATORY & ZONING (8 data points)")
    print("-" * 100)
    with tracker.track("regulatory_total"):
        regulatory_data = await regulatory.collect(address, radius_miles=1.0)
        
    print(f"   Total time: {tracker.metrics[-1].duration_ms:.2f} ms")
    print(f"   Data points collected: 8")
    print(f"   Jurisdiction: {regulatory_data.get('jurisdiction', 'N/A')}, {regulatory_data.get('state', 'N/A')}")
    print(f"   Source: {regulatory_data.get('data_source', 'N/A')}\n")
    
    results["regulatory"] = regulatory_data
    
    # Generate XAI explanations
    print("\n" + "="*100)
    print("GENERATING XAI EXPLANATIONS FOR ALL 66 DATA POINTS")
    print("="*100)
    
    with tracker.track("xai_generation"):
        xai_explanations = generate_xai_explanations(results)
    
    print(f"✓ XAI explanations generated: {tracker.metrics[-1].duration_ms:.2f} ms\n")
    
    # Get performance report
    performance_report = tracker.get_report()
    
    # Display sample XAI explanations (top 10 data points)
    print("\n" + "="*100)
    print("SAMPLE XAI EXPLANATIONS (10 Key Data Points)")
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
        if category in xai_explanations and point_name in xai_explanations[category]:
            exp = xai_explanations[category][point_name]
            print(f"\n{'─'*100}")
            print(f"📍 {exp['data_point'].replace('_', ' ').title()}")
            print(f"{'─'*100}")
            print(f"   Value: {exp['value']}")
            print(f"   Category: {exp['category'].title()}")
            print(f"   ")
            print(f"   What: {exp['explanation']['what']}")
            print(f"   How:  {exp['explanation']['how']}")
            print(f"   Why:  {exp['explanation']['why']}")
            print(f"   ")
            print(f"   Source: {exp['explanation']['source']}")
            print(f"   Confidence: {exp['explanation']['confidence']}")
            print(f"   Interpretation: {exp['interpretation']}")
    
    # Display timing breakdown
    print("\n\n" + "="*100)
    print("DETAILED TIMING BREAKDOWN")
    print("="*100)
    
    print(f"\nTotal Analysis Time: {performance_report['total_time_ms']:.2f} ms ({performance_report['total_time_ms']/1000:.2f} seconds)")
    print(f"Tracked Operations: {performance_report['tracked_time_ms']:.2f} ms")
    print(f"Overhead: {performance_report['overhead_ms']:.2f} ms")
    print(f"Steps Executed: {performance_report['steps_count']} ({performance_report['successful_steps']} successful)")
    
    print("\n" + "-"*100)
    print("Category Timing Breakdown:")
    print("-"*100)
    
    for category, data in sorted(performance_report['categories'].items(), 
                                 key=lambda x: x[1]['total_ms'], 
                                 reverse=True):
        print(f"  {category.upper():.<40} {data['total_ms']:>10.2f} ms ({data['count']} steps)")
    
    print("\n" + "-"*100)
    print("Step-by-Step Timing:")
    print("-"*100)
    
    for step in performance_report['detailed_steps']:
        status = "✓" if step['success'] else "✗"
        print(f"  {status} {step['step']:.<50} {step['duration_ms']:>10.2f} ms")
    
    # Calculate category scores
    print("\n\n" + "="*100)
    print("CATEGORY SCORES WITH XAI JUSTIFICATIONS")
    print("="*100)
    
    scores = calculate_scores(results)
    
    for category, score in scores.items():
        if category != "overall":
            category_explanation = DataPointExplainer.generate_category_explanation(
                category,
                results.get(category, {}),
                score
            )
            
            print(f"\n{'─'*100}")
            print(f"📊 {category.upper().replace('_', ' ')}: {score:.1f}/100")
            print(f"{'─'*100}")
            print(f"   {category_explanation['interpretation']}")
            print(f"   ")
            print(f"   Key Drivers:")
            for driver, description in category_explanation['key_drivers'][:3]:
                value = results.get(category, {}).get(driver, "N/A")
                print(f"     • {description}: {value}")
            print(f"   ")
            print(f"   Recommendation:")
            print(f"     {category_explanation['recommendation']}")
    
    print(f"\n{'='*100}")
    print(f"OVERALL SCORE: {scores['overall']:.1f}/100")
    print(f"{'='*100}")
    
    if scores['overall'] >= 75:
        recommendation = "EXCELLENT ⭐⭐⭐⭐⭐ - Highly recommended location"
    elif scores['overall'] >= 60:
        recommendation = "GOOD ⭐⭐⭐⭐ - Suitable location with minor considerations"
    elif scores['overall'] >= 45:
        recommendation = "FAIR ⭐⭐⭐ - Viable with improvements"
    else:
        recommendation = "POOR ⭐⭐ - Not recommended"
    
    print(f"\n🎯 FINAL RECOMMENDATION: {recommendation}\n")
    
    # Compile comprehensive output
    output = {
        "address": address,
        "timestamp": datetime.now().isoformat(),
        "total_analysis_time_ms": performance_report['total_time_ms'],
        "total_analysis_time_seconds": round(performance_report['total_time_ms'] / 1000, 2),
        "data_points_collected": 66,
        "categories": {
            "demographics": {
                "data": results["demographics"],
                "score": scores.get("demographics", 0),
                "data_points": 15,
                "collection_time_ms": next(
                    (s['duration_ms'] for s in performance_report['detailed_steps'] 
                     if s['step'] == 'demographics_total'), 0
                )
            },
            "competition": {
                "data": results["competition"],
                "score": scores.get("competition", 0),
                "data_points": 12,
                "collection_time_ms": next(
                    (s['duration_ms'] for s in performance_report['detailed_steps'] 
                     if s['step'] == 'competition_total'), 0
                )
            },
            "accessibility": {
                "data": results["accessibility"],
                "score": scores.get("accessibility", 0),
                "data_points": 10,
                "collection_time_ms": next(
                    (s['duration_ms'] for s in performance_report['detailed_steps'] 
                     if s['step'] == 'accessibility_total'), 0
                )
            },
            "safety": {
                "data": results["safety"],
                "score": scores.get("safety", 0),
                "data_points": 11,
                "collection_time_ms": next(
                    (s['duration_ms'] for s in performance_report['detailed_steps'] 
                     if s['step'] == 'safety_total'), 0
                )
            },
            "economic": {
                "data": results["economic"],
                "score": scores.get("economic", 0),
                "data_points": 10,
                "collection_time_ms": next(
                    (s['duration_ms'] for s in performance_report['detailed_steps'] 
                     if s['step'] == 'economic_total'), 0
                )
            },
            "regulatory": {
                "data": results["regulatory"],
                "score": scores.get("regulatory", 0),
                "data_points": 8,
                "collection_time_ms": next(
                    (s['duration_ms'] for s in performance_report['detailed_steps'] 
                     if s['step'] == 'regulatory_total'), 0
                )
            }
        },
        "scores": scores,
        "recommendation": recommendation,
        "xai_explanations": xai_explanations,
        "performance_report": performance_report
    }
    
    return output


def generate_xai_explanations(results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate XAI explanations for all data points"""
    
    explanations = {}
    
    category_mapping = {
        "demographics": results.get("demographics", {}),
        "competition": results.get("competition", {}),
        "accessibility": results.get("accessibility", {}),
        "safety": results.get("safety", {}),
        "economic": results.get("economic", {}),
        "regulatory": results.get("regulatory", {})
    }
    
    for category, data in category_mapping.items():
        explanations[category] = {}
        
        for key, value in data.items():
            # Skip metadata fields
            if key in ["success", "address", "coordinates", "data_source", "note",
                      "jurisdiction", "state", "centers_details", "radius_miles",
                      "search_radius_miles", "centers_analyzed", "total_population",
                      "land_area_sqmi"]:
                continue
            
            # Generate explanation
            explanation = DataPointExplainer.explain_data_point(
                category, key, value, data
            )
            explanations[category][key] = explanation
    
    return explanations


def calculate_scores(results: Dict[str, Any]) -> Dict[str, float]:
    """Calculate category scores (0-100)"""
    
    scores = {}
    
    # Demographics
    demo = results.get("demographics", {})
    if demo:
        demo_score = (
            min(100, demo.get("population_density", 0) / 10) * 0.2 +
            min(100, demo.get("median_household_income", 0) / 1000) * 0.2 +
            min(100, demo.get("dual_income_rate", 0)) * 0.2 +
            min(100, demo.get("family_household_rate", 0)) * 0.2 +
            min(100, demo.get("birth_rate", 0) * 5) * 0.2
        )
        scores["demographics"] = round(demo_score, 1)
    
    # Competition
    comp = results.get("competition", {})
    if comp:
        comp_score = (
            (100 - min(100, comp.get("market_saturation_index", 0) * 20)) * 0.35 +
            comp.get("market_gap_score", 50) * 0.35 +
            (100 - min(100, comp.get("competitive_intensity_score", 0))) * 0.3
        )
        scores["competition"] = round(comp_score, 1)
    
    # Accessibility
    acc = results.get("accessibility", {})
    if acc:
        acc_score = (
            acc.get("transit_score", 50) * 0.3 +
            acc.get("morning_rush_score", 50) * 0.3 +
            acc.get("parking_availability_score", 50) * 0.2 +
            acc.get("highway_visibility_score", 50) * 0.2
        )
        scores["accessibility"] = round(acc_score, 1)
    
    # Safety
    safe = results.get("safety", {})
    if safe:
        safe_score = (
            (100 - safe.get("crime_rate_index", 30)) * 0.3 +
            safe.get("pedestrian_safety_score", 70) * 0.2 +
            (100 - min(100, safe.get("air_quality_index", 50) / 2)) * 0.2 +
            safe.get("neighborhood_safety_perception", 60) * 0.3
        )
        scores["safety"] = round(safe_score, 1)
    
    # Economic
    econ = results.get("economic", {})
    if econ:
        econ_score = (
            (100 - min(100, econ.get("real_estate_cost_per_sqft", 150) / 4)) * 0.3 +
            econ.get("childcare_worker_availability_score", 60) * 0.3 +
            econ.get("business_incentives_score", 50) * 0.2 +
            econ.get("economic_growth_indicator", 55) * 0.2
        )
        scores["economic"] = round(econ_score, 1)
    
    # Regulatory
    reg = results.get("regulatory", {})
    if reg:
        reg_score = (
            reg.get("zoning_compliance_score", 60) * 0.4 +
            reg.get("rezoning_feasibility_score", 65) * 0.2 +
            (100 - min(100, reg.get("building_code_complexity_score", 55))) * 0.2 +
            (100 - min(100, reg.get("licensing_difficulty_score", 55))) * 0.2
        )
        scores["regulatory"] = round(reg_score, 1)
    
    # Overall weighted score
    weights = {"demographics": 90, "competition": 75, "accessibility": 65,
               "safety": 70, "economic": 55, "regulatory": 50}
    
    total_weight = sum(weights.values())
    weighted_sum = sum(scores.get(cat, 0) * weight for cat, weight in weights.items())
    scores["overall"] = round(weighted_sum / total_weight, 1)
    
    return scores


async def main():
    """Main execution"""
    
    # Test address
    address = "1600 Amphitheatre Parkway, Mountain View, CA 94043"  # Google HQ
    
    try:
        # Run analysis
        output = await collect_with_timing_and_xai(address)
        
        # Save to JSON
        filename = f"analysis_with_timing_xai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n{'='*100}")
        print(f"✅ Complete analysis saved to: {filename}")
        print(f"   Total size: 66 data points + XAI explanations + timing data")
        print(f"   Total time: {output['total_analysis_time_seconds']} seconds")
        print(f"{'='*100}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting 66-point analysis with millisecond timing and XAI...")
    asyncio.run(main())
