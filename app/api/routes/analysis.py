"""
Analysis API Routes
Handles location analysis requests from the dashboard
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
from datetime import datetime

from app.core.data_collectors.tiles.demographics import TilesDemographicsCollector
from app.core.data_collectors.tiles.competition import TilesCompetitionCollector
from app.core.data_collectors.tiles.accessibility import TilesAccessibilityCollector
from app.core.data_collectors.safety_enhanced import SafetyCollectorEnhanced
from app.core.data_collectors.tiles.economic import TilesEconomicCollector
from app.core.data_collectors.tiles.regulatory import TilesRegulatoryCollector
from app.utils.timing_xai import PerformanceTracker


router = APIRouter(prefix="/api/v1", tags=["Analysis"])


class AnalysisRequest(BaseModel):
    """Location analysis request"""
    address: str = Field(..., description="Full street address")
    radius_miles: float = Field(default=2.0, ge=0.5, le=10.0, description="Search radius in miles")


class AnalysisResponse(BaseModel):
    """Location analysis response"""
    address: str
    timestamp: str
    total_analysis_time_ms: float
    total_analysis_time_seconds: float
    data_points_collected: int
    overall_score: float
    recommendation: str
    categories: dict
    performance_report: dict


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_location(request: AnalysisRequest):
    """
    Analyze a location with 66 data points
    
    **Input:**
    - address: Full street address (e.g., "1600 Amphitheatre Parkway, Mountain View, CA 94043")
    - radius_miles: Search radius (default: 2.0 miles)
    
    **Output:**
    - Overall score (0-100)
    - 6 category scores with detailed data
    - 66 individual data points
    - Performance timing metrics
    - AI-driven recommendations
    
    **Categories:**
    1. Demographics (15 points) - Population, income, family composition
    2. Competition (12 points) - Existing centers, market saturation
    3. Accessibility (10 points) - Transit, commute times, parking
    4. Safety (11 points) - Crime rates, environmental health
    5. Economic (10 points) - Real estate costs, labor availability
    6. Regulatory (8 points) - Zoning, licensing, permits
    
    **Data Sources:**
    - U.S. Census Bureau API
    - Google Maps Platform APIs
    - EPA/FBI Databases
    - BLS Economic Data
    """
    
    tracker = PerformanceTracker()
    
    try:
        # Initialize collectors
        with tracker.track("initialization"):
            demographics = TilesDemographicsCollector()
            competition = TilesCompetitionCollector()
            accessibility = TilesAccessibilityCollector()
            safety = SafetyCollectorEnhanced()
            economic = TilesEconomicCollector()
            regulatory = TilesRegulatoryCollector()
        
        results = {}
        
        # Collect demographics (15 points)
        with tracker.track("demographics_total"):
            demographics_data = await demographics.collect(request.address, radius_miles=request.radius_miles)
            results["demographics"] = demographics_data
        
        # Collect competition (12 points)
        with tracker.track("competition_total"):
            competition_data = await competition.collect(request.address, radius_miles=request.radius_miles)
            results["competition"] = competition_data
        
        # Collect accessibility (10 points)
        with tracker.track("accessibility_total"):
            accessibility_data = await accessibility.collect(request.address, radius_miles=5.0)
            results["accessibility"] = accessibility_data
        
        # Collect safety (11 points)
        with tracker.track("safety_total"):
            safety_data = await safety.collect(request.address, radius_miles=1.0)
            results["safety"] = safety_data
        
        # Collect economic (10 points)
        with tracker.track("economic_total"):
            economic_data = await economic.collect(request.address, radius_miles=request.radius_miles)
            results["economic"] = economic_data
        
        # Collect regulatory (8 points)
        with tracker.track("regulatory_total"):
            regulatory_data = await regulatory.collect(request.address, radius_miles=1.0)
            results["regulatory"] = regulatory_data
        
        # Calculate scores
        with tracker.track("score_calculation"):
            scores = calculate_scores(results)
        
        # Get performance report
        performance_report = tracker.get_report()
        
        # Build response with flattened category structure
        response_data = {
            "address": request.address,
            "timestamp": datetime.now().isoformat(),
            "total_analysis_time_ms": performance_report['total_time_ms'],
            "total_analysis_time_seconds": round(performance_report['total_time_ms'] / 1000, 2),
            "data_points_collected": 66,
            "overall_score": scores.get("overall", 0),
            "recommendation": get_recommendation(scores.get("overall", 0)),
            "categories": {
                "demographics": {
                    **results["demographics"],  # Flatten data directly into category
                    "score": scores.get("demographics", 0),
                    "metrics_count": 15,
                    "collection_time_ms": next(
                        (s['duration_ms'] for s in performance_report['detailed_steps'] 
                         if s['step'] == 'demographics_total'), 0
                    )
                },
                "competition": {
                    **results["competition"],  # Flatten data directly into category
                    "score": scores.get("competition", 0),
                    "metrics_count": 12,
                    "collection_time_ms": next(
                        (s['duration_ms'] for s in performance_report['detailed_steps'] 
                         if s['step'] == 'competition_total'), 0
                    )
                },
                "accessibility": {
                    **results["accessibility"],  # Flatten data directly into category
                    "score": scores.get("accessibility", 0),
                    "metrics_count": 10,
                    "collection_time_ms": next(
                        (s['duration_ms'] for s in performance_report['detailed_steps'] 
                         if s['step'] == 'accessibility_total'), 0
                    )
                },
                "safety": {
                    **results["safety"],  # Flatten data directly into category
                    "score": scores.get("safety", 0),
                    "metrics_count": 11,
                    "collection_time_ms": next(
                        (s['duration_ms'] for s in performance_report['detailed_steps'] 
                         if s['step'] == 'safety_total'), 0
                    )
                },
                "economic": {
                    **results["economic"],  # Flatten data directly into category
                    "score": scores.get("economic", 0),
                    "metrics_count": 10,
                    "collection_time_ms": next(
                        (s['duration_ms'] for s in performance_report['detailed_steps'] 
                         if s['step'] == 'economic_total'), 0
                    )
                },
                "regulatory": {
                    **results["regulatory"],  # Flatten data directly into category
                    "score": scores.get("regulatory", 0),
                    "metrics_count": 8,
                    "collection_time_ms": next(
                        (s['duration_ms'] for s in performance_report['detailed_steps'] 
                         if s['step'] == 'regulatory_total'), 0
                    )
                }
            },
            "performance_report": performance_report
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def calculate_scores(results: dict) -> dict:
    """Calculate category scores (0-100)"""
    
    scores = {}
    
    # Demographics (Tiles focused: Homeownership + Income)
    demo = results.get("demographics", {})
    if demo:
        income_score = min(100, demo.get("median_household_income", 0) / 1200) # 120k = 100
        home_score = demo.get("homeownership_rate", 0)
        renov_score = min(100, demo.get("renovation_potential_rate", 0) * 2)
        demo_score = (income_score * 0.4 + home_score * 0.3 + renov_score * 0.3)
        scores["demographics"] = round(demo_score, 1)
    
    # Competition (Tiles focused: Saturation)
    comp = results.get("competition", {})
    if comp:
        saturation = comp.get("market_saturation", "LOW")
        if saturation == "LOW": comp_score = 90.0
        elif saturation == "MEDIUM": comp_score = 60.0
        else: comp_score = 30.0
        scores["competition"] = round(comp_score, 1)
    
    # Accessibility (Tiles focused: Logistics + Access)
    acc = results.get("accessibility", {})
    if acc:
        acc_score = (
            acc.get("truck_accessibility_score", 60) * 0.4 +
            acc.get("loading_dock_feasibility", 50) * 0.3 +
            acc.get("parking_capacity_index", 50) * 0.15 +
            acc.get("signage_visibility", 50) * 0.15
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
    
    # Economic (Tiles focused: Real estate + Installers)
    econ = results.get("economic", {})
    if econ:
        econ_score = (
            (100 - min(100, econ.get("real_estate_cost_per_sqft", 140) / 3.5)) * 0.3 +
            econ.get("installer_availability_score", 60) * 0.3 +
            econ.get("business_incentives_score", 50) * 0.2 +
            econ.get("economic_growth_indicator", 55) * 0.2
        )
        scores["economic"] = round(econ_score, 1)
    
    # Regulatory (Tiles focused: Zoning + Permitting)
    reg = results.get("regulatory", {})
    if reg:
        reg_score = (
            reg.get("zoning_compliance_score", 60) * 0.4 +
            reg.get("rezoning_feasibility_score", 65) * 0.2 +
            (100 - min(100, reg.get("building_code_complexity", 50))) * 0.2 +
            (100 - min(100, reg.get("licensing_difficulty", 50))) * 0.2
        )
        scores["regulatory"] = round(reg_score, 1)
    
    # Overall weighted score
    weights = {"demographics": 90, "competition": 75, "accessibility": 65,
               "safety": 70, "economic": 55, "regulatory": 50}
    
    total_weight = sum(weights.values())
    weighted_sum = sum(scores.get(cat, 0) * weight for cat, weight in weights.items())
    scores["overall"] = round(weighted_sum / total_weight, 1)
    
    return scores


def get_recommendation(score: float) -> str:
    """Get recommendation text based on score"""
    
    if score >= 75:
        return "Excellent location for a tiles dealer or distribution center"
    elif score >= 60:
        return "Suitable location with good potential - Minor considerations"
    elif score >= 45:
        return "Viable location with improvements needed - Moderate risk"
    else:
        return "Not recommended - Significant challenges identified"
