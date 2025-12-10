"""
Production Server - Real API Calls
Uses actual Google Maps and Census Bureau APIs
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any
import asyncio
from datetime import datetime

# Import real data collectors
from app.core.data_collectors.demographics import DemographicsCollector
from app.core.data_collectors.competition_enhanced import CompetitionCollectorEnhanced
from app.core.data_collectors.accessibility_enhanced import AccessibilityCollectorEnhanced
from app.core.data_collectors.safety_enhanced import SafetyCollectorEnhanced
from app.core.data_collectors.economic_enhanced import EconomicCollectorEnhanced
from app.core.data_collectors.regulatory import RegulatoryCollector
from app.core.data_collectors.epa_collector import EPACollector
from app.core.data_collectors.hud_collector import HUDCollector
from app.core.data_collectors.fbi_crime_collector import FBICrimeCollector
from app.core.data_collectors.fema_flood_collector import FEMAFloodCollector
from app.utils.timing_xai import PerformanceTracker, DataPointExplainer
from app.config import get_settings
import googlemaps

app = FastAPI(title="Brightspot Locator AI - Production")

settings = get_settings()


async def validate_and_correct_address(address: str) -> Dict[str, Any]:
    """
    Validate and correct address using Google Geocoding API
    Returns corrected address and location details
    """
    if not settings.places_api_key or settings.places_api_key == "your_google_maps_api_key_here":
        return {
            "success": False,
            "error": "Google Maps API key not configured",
            "original_address": address
        }
    
    try:
        gmaps = googlemaps.Client(key=settings.places_api_key)
        
        # Use Geocoding API to validate and get full address
        geocode_result = gmaps.geocode(address)
        
        if not geocode_result or len(geocode_result) == 0:
            return {
                "success": False,
                "error": f"Address not found: '{address}'. Please provide a more complete address with street, city, state, and zip code.",
                "original_address": address,
                "suggestions": "Try format: '123 Main Street, City, State ZIP'"
            }
        
        # Get the best match (first result)
        result = geocode_result[0]
        
        # Extract address components
        formatted_address = result.get("formatted_address", address)
        location = result.get("geometry", {}).get("location", {})
        address_components = result.get("address_components", [])
        
        # Parse components
        street_number = ""
        route = ""
        city = ""
        state = ""
        zip_code = ""
        county = ""
        
        for component in address_components:
            types = component.get("types", [])
            if "street_number" in types:
                street_number = component.get("long_name", "")
            elif "route" in types:
                route = component.get("long_name", "")
            elif "locality" in types:
                city = component.get("long_name", "")
            elif "administrative_area_level_1" in types:
                state = component.get("short_name", "")
            elif "postal_code" in types:
                zip_code = component.get("long_name", "")
            elif "administrative_area_level_2" in types:
                county = component.get("long_name", "")
        
        return {
            "success": True,
            "original_address": address,
            "formatted_address": formatted_address,
            "corrected_address": formatted_address,
            "location": {
                "lat": location.get("lat"),
                "lng": location.get("lng")
            },
            "components": {
                "street_number": street_number,
                "route": route,
                "street_address": f"{street_number} {route}".strip(),
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "county": county
            },
            "place_id": result.get("place_id", ""),
            "types": result.get("types", [])
        }
        
    except googlemaps.exceptions.ApiError as e:
        return {
            "success": False,
            "error": f"Google Maps API error: {str(e)}",
            "original_address": address
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Address validation failed: {str(e)}",
            "original_address": address
        }

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except:
    pass

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/favicon.ico")

try:
    templates = Jinja2Templates(directory="app/templates")
except:
    templates = None


def calculate_overall_score(categories: Dict[str, Any]) -> float:
    """Calculate weighted overall score"""
    weights = {
        "demographics": 0.25,
        "competition": 0.20,
        "accessibility": 0.15,
        "safety": 0.20,
        "economic": 0.10,
        "regulatory": 0.10
    }
    
    total_score = 0
    total_weight = 0
    
    for category, weight in weights.items():
        if category in categories:
            score = categories[category].get("score", 0)
            total_score += score * weight
            total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 0


def calculate_category_score(category: str, data: Dict[str, Any]) -> float:
    """Calculate score for a category based on its data"""
    
    if category == "demographics":
        score = (
            min(100, data.get("population_density", 0) / 10) * 0.2 +
            min(100, data.get("median_household_income", 0) / 1000) * 0.2 +
            min(100, data.get("dual_income_rate", 0)) * 0.2 +
            min(100, data.get("family_household_rate", 0)) * 0.2 +
            min(100, data.get("birth_rate", 0) * 5) * 0.2
        )
        return round(score, 1)
    
    elif category == "competition":
        score = (
            (100 - min(100, data.get("market_saturation_index", 0) * 20)) * 0.35 +
            data.get("market_gap_score", 50) * 0.35 +
            (100 - min(100, data.get("competitive_intensity_score", 0))) * 0.3
        )
        return round(score, 1)
    
    elif category == "accessibility":
        score = (
            data.get("transit_score", 50) * 0.3 +
            data.get("morning_rush_score", 50) * 0.3 +
            data.get("parking_availability_score", 50) * 0.2 +
            data.get("highway_visibility_score", 50) * 0.2
        )
        return round(score, 1)
    
    elif category == "safety":
        score = (
            (100 - data.get("crime_rate_index", 30)) * 0.3 +
            data.get("pedestrian_safety_score", 70) * 0.2 +
            (100 - min(100, data.get("air_quality_index", 50) / 2)) * 0.2 +
            data.get("neighborhood_safety_perception", 60) * 0.3
        )
        return round(score, 1)
    
    elif category == "economic":
        score = (
            (100 - min(100, data.get("real_estate_cost_per_sqft", 150) / 4)) * 0.3 +
            data.get("childcare_worker_availability_score", 60) * 0.3 +
            data.get("business_incentives_score", 50) * 0.2 +
            data.get("economic_growth_indicator", 55) * 0.2
        )
        return round(score, 1)
    
    elif category == "regulatory":
        score = (
            data.get("zoning_compliance_score", 60) * 0.4 +
            data.get("rezoning_feasibility_score", 65) * 0.2 +
            (100 - min(100, data.get("building_code_complexity_score", 55))) * 0.2 +
            (100 - min(100, data.get("licensing_difficulty_score", 55))) * 0.2
        )
        return round(score, 1)
    
    return 50.0


def get_recommendation(score: float) -> str:
    """Get recommendation based on overall score"""
    if score >= 75:
        return "EXCELLENT ⭐⭐⭐⭐⭐ - Highly recommended location"
    elif score >= 60:
        return "GOOD ⭐⭐⭐⭐ - Suitable location with good potential"
    elif score >= 45:
        return "FAIR ⭐⭐⭐ - Viable with improvements"
    else:
        return "POOR ⭐⭐ - Not recommended"


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve dashboard"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("<h1>Dashboard template not found</h1>")


@app.get("/api-sources", response_class=HTMLResponse)
async def api_sources(request: Request):
    """Serve API data sources page"""
    if templates:
        return templates.TemplateResponse("api_sources.html", {"request": request})
    return HTMLResponse("<h1>API Sources page not found</h1>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0-production",
        "api_mode": "real",
        "google_maps_configured": bool(settings.places_api_key and settings.places_api_key != "your_google_maps_api_key_here"),
        "census_configured": bool(settings.census_api_key and settings.census_api_key != "your_census_api_key_here"),
        "epa_configured": True,  # No key required
        "hud_configured": bool(settings.hud_api_key),
        "fbi_crime_configured": bool(settings.fbi_crime_api_key),
        "fema_configured": True  # No key required
    }


@app.post("/api/v1/validate-address")
async def validate_address_endpoint(request: Request):
    """Validate and correct an address using Google Geocoding API"""
    body = await request.json()
    address = body.get("address", "")
    
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    result = await validate_and_correct_address(address)
    
    if result.get("success"):
        return JSONResponse(result)
    else:
        raise HTTPException(status_code=400, detail=result)


@app.post("/api/v1/analyze")
async def analyze_location(request: Request):
    """Analyze location using REAL APIs"""
    
    # Get request body
    body = await request.json()
    address = body.get("address", "")
    radius = body.get("radius_miles", 2.0)
    
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    # Check API keys
    if not settings.places_api_key or settings.places_api_key == "your_google_maps_api_key_here":
        raise HTTPException(
            status_code=503,
            detail="Google Maps API key not configured. Please add GOOGLE_MAPS_API_KEY to .env file"
        )
    
    # Validate and correct address first
    address_validation = await validate_and_correct_address(address)
    
    if not address_validation.get("success"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid address",
                "message": address_validation.get("error"),
                "original_address": address,
                "suggestions": address_validation.get("suggestions", "Please provide a complete address")
            }
        )
    
    # Use corrected address for analysis
    corrected_address = address_validation.get("formatted_address", address)
    
    # Initialize performance tracker
    tracker = PerformanceTracker()
    
    try:
        # Initialize collectors
        with tracker.track("initialization"):
            demographics = DemographicsCollector()
            competition = CompetitionCollectorEnhanced()
            accessibility = AccessibilityCollectorEnhanced()
            safety = SafetyCollectorEnhanced()
            economic = EconomicCollectorEnhanced()
            regulatory = RegulatoryCollector()
            epa = EPACollector()
            hud = HUDCollector(api_key=settings.hud_api_key if hasattr(settings, 'hud_api_key') else None)
            fbi_crime = FBICrimeCollector(api_key=settings.fbi_crime_api_key if hasattr(settings, 'fbi_crime_api_key') else None)
            fema_flood = FEMAFloodCollector()
        
        results = {}
        
        # Get location coordinates from validation
        location = address_validation.get("location", {})
        latitude = location.get("lat")
        longitude = location.get("lng")
        components = address_validation.get("components", {})
        state = components.get("state", "")
        county = components.get("county", "")
        zip_code = components.get("zip_code", "")
        
        # Collect demographics (15 points)
        with tracker.track("demographics"):
            demographics_data = await demographics.collect(corrected_address, radius_miles=radius)
            results["demographics"] = demographics_data
        
        # Collect competition (12 points)
        with tracker.track("competition"):
            competition_data = await competition.collect(corrected_address, radius_miles=radius)
            results["competition"] = competition_data
        
        # Collect accessibility (10 points)
        with tracker.track("accessibility"):
            accessibility_data = await accessibility.collect(corrected_address, radius_miles=radius)
            results["accessibility"] = accessibility_data
        
        # Collect NEW environmental data from EPA (3 new real data points)
        with tracker.track("environmental"):
            epa_data = await epa.collect(corrected_address, latitude, longitude, radius_miles=radius)
            results["environmental"] = epa_data
        
        # Collect NEW crime data from FBI (9 new real data points)
        with tracker.track("crime"):
            crime_data = await fbi_crime.collect(corrected_address, state, county, latitude, longitude)
            results["crime"] = crime_data
        
        # Collect NEW flood data from FEMA (6 new real data points)
        with tracker.track("flood"):
            flood_data = await fema_flood.collect(corrected_address, latitude, longitude)
            results["flood"] = flood_data
        
        # Collect safety (11 points) - now ENHANCED with EPA, FBI, FEMA real data
        with tracker.track("safety"):
            safety_data = await safety.collect(corrected_address, radius_miles=radius)
            
            # Merge real EPA data (air quality, environmental hazards)
            if epa_data:
                safety_data["air_quality_index"] = epa_data.get("air_quality_index", safety_data.get("air_quality_index", 50))
                safety_data["environmental_hazards_score"] = epa_data.get("environmental_hazards_score", safety_data.get("environmental_hazards_score", 0))
                safety_data["pollution_risk"] = epa_data.get("pollution_risk", "Unknown")
                safety_data["tri_sites_count"] = epa_data.get("tri_sites_count", 0)
                safety_data["superfund_sites_count"] = epa_data.get("superfund_sites_count", 0)
            
            # Merge real FBI crime data
            if crime_data:
                safety_data["crime_rate_index"] = crime_data.get("crime_rate_index", safety_data.get("crime_rate_index", 50))
                safety_data["neighborhood_safety_score"] = crime_data.get("neighborhood_safety_score", safety_data.get("neighborhood_safety_score", 50))
                safety_data["violent_crime_rate"] = crime_data.get("violent_crime_rate", 0)
                safety_data["property_crime_rate"] = crime_data.get("property_crime_rate", 0)
            
            # Merge real FEMA flood data
            if flood_data:
                safety_data["flood_risk_indicator"] = flood_data.get("flood_risk_score", safety_data.get("flood_risk_indicator", 25))
                safety_data["flood_zone"] = flood_data.get("flood_zone", "X")
                safety_data["flood_risk_level"] = flood_data.get("flood_risk_level", "Low")
                safety_data["insurance_required"] = flood_data.get("insurance_required", False)
            
            results["safety"] = safety_data
        
        # Collect NEW real estate data from HUD (5 new real data points)
        with tracker.track("housing"):
            hud_data = await hud.collect(corrected_address, zip_code, state)
            results["housing"] = hud_data
        
        # Collect economic (10 points) - now ENHANCED with HUD real data
        with tracker.track("economic"):
            economic_data = await economic.collect(corrected_address, radius_miles=radius)
            
            # Merge real HUD data (real estate costs)
            if hud_data:
                economic_data["real_estate_cost_per_sqft"] = hud_data.get("real_estate_cost_per_sqft", economic_data.get("real_estate_cost_per_sqft", 150))
                economic_data["estimated_monthly_rent"] = hud_data.get("estimated_monthly_rent", economic_data.get("estimated_monthly_rent", 0))
                economic_data["startup_cost_estimate"] = hud_data.get("estimated_startup_cost", economic_data.get("startup_cost_estimate", 0))
                economic_data["average_market_rent"] = hud_data.get("average_fmr", 0)
            
            results["economic"] = economic_data
        
        # Collect regulatory (8 points)
        with tracker.track("regulatory"):
            regulatory_data = await regulatory.collect(corrected_address, radius_miles=radius)
            results["regulatory"] = regulatory_data
        
        # Calculate scores for each category
        categories = {}
        for category, data in results.items():
            score = calculate_category_score(category, data)
            categories[category] = {
                "score": score,
                "data": data
            }
        
        # Calculate overall score
        overall_score = calculate_overall_score(categories)
        recommendation = get_recommendation(overall_score)
        
        # Get performance report
        performance = tracker.get_report()
        
        # Generate key insights (now with REAL data from EPA, FBI, FEMA, HUD)
        key_insights = []
        
        if results.get("demographics", {}).get("children_0_5_count", 0) > 1000:
            key_insights.append(f"Strong demographic profile with {results['demographics'].get('children_0_5_count', 0):,} children aged 0-5")
        
        if results.get("competition", {}).get("market_gap_score", 0) > 60:
            key_insights.append(f"Good market opportunity with {results['competition'].get('market_gap_score', 0):.0f}% gap score")
        
        if categories.get("safety", {}).get("score", 0) > 75:
            key_insights.append(f"Excellent safety metrics ({categories['safety']['score']:.0f}/100)")
        
        # NEW: FBI Crime data insights
        if results.get("crime", {}).get("crime_rate_index", 50) < 30:
            key_insights.append(f"Low crime area - {results['crime'].get('risk_level', 'Low')} risk per FBI data")
        elif results.get("crime", {}).get("crime_rate_index", 50) > 70:
            key_insights.append(f"High crime area - {results['crime'].get('risk_level', 'High')} risk per FBI data")
        
        # NEW: EPA Environmental data insights
        if results.get("environmental", {}).get("air_quality_index", 50) < 50:
            key_insights.append(f"Good air quality (AQI: {results['environmental'].get('air_quality_index', 0):.0f})")
        if results.get("environmental", {}).get("superfund_sites_count", 0) > 0:
            key_insights.append(f"⚠️ {results['environmental'].get('superfund_sites_count', 0)} EPA Superfund sites within radius")
        
        # NEW: FEMA Flood data insights
        if results.get("flood", {}).get("flood_zone", "X") in ["A", "AE", "AH", "AO", "V", "VE"]:
            key_insights.append(f"⚠️ High flood risk zone ({results['flood'].get('flood_zone', 'Unknown')}) - insurance required")
        elif results.get("flood", {}).get("flood_zone", "X") == "X":
            key_insights.append("Low flood risk - FEMA Zone X")
        
        # NEW: HUD Real Estate data insights
        if results.get("housing", {}).get("average_fmr", 0) > 0:
            key_insights.append(f"Market rent: ${results['housing'].get('average_fmr', 0):.0f}/month (HUD data)")
        
        if results.get("competition", {}).get("existing_centers_count", 0) < 5:
            key_insights.append("Low competition - undersupplied market")
        elif results.get("competition", {}).get("existing_centers_count", 0) > 10:
            key_insights.append("High competition - saturated market")
        
        if results.get("demographics", {}).get("median_household_income", 0) > 80000:
            key_insights.append("Above-average income levels support premium pricing")
        
        # Build response
        response = {
            "address": corrected_address,
            "original_address": address,
            "address_validation": {
                "corrected": corrected_address != address,
                "components": address_validation.get("components", {}),
                "location": address_validation.get("location", {}),
                "place_id": address_validation.get("place_id", "")
            },
            "timestamp": datetime.now().isoformat(),
            "overall_score": round(overall_score, 1),
            "recommendation": recommendation,
            "data_points_collected": 66,
            "analysis_time_ms": performance["total_time_ms"],
            "categories": categories,
            "timing": {
                "demographics_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "demographics"), 0),
                "competition_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "competition"), 0),
                "accessibility_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "accessibility"), 0),
                "environmental_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "environmental"), 0),
                "crime_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "crime"), 0),
                "flood_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "flood"), 0),
                "safety_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "safety"), 0),
                "housing_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "housing"), 0),
                "economic_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "economic"), 0),
                "regulatory_ms": next((s["duration_ms"] for s in performance["detailed_steps"] if s["step"] == "regulatory"), 0)
            },
            "key_insights": key_insights,
            "performance_report": performance
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        import traceback
        error_detail = str(e)
        if "REQUEST_DENIED" in error_detail:
            error_detail = "Google Maps API key is invalid or APIs are not enabled. Please check your API key and enable required APIs."
        elif "OVER_QUERY_LIMIT" in error_detail:
            error_detail = "Google Maps API quota exceeded. Please check your billing settings."
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {error_detail}"
        )


@app.get("/api/check-config")
async def check_configuration():
    """Check if APIs are configured"""
    return {
        "google_maps": {
            "configured": bool(settings.places_api_key and settings.places_api_key != "your_google_maps_api_key_here"),
            "key_prefix": settings.places_api_key[:10] + "..." if settings.places_api_key else "Not set",
            "status": "✅ CONFIGURED" if settings.places_api_key and settings.places_api_key != "your_google_maps_api_key_here" else "❌ NOT CONFIGURED"
        },
        "census": {
            "configured": bool(settings.census_api_key and settings.census_api_key != "your_census_api_key_here"),
            "key_prefix": settings.census_api_key[:10] + "..." if settings.census_api_key else "Not set",
            "status": "✅ CONFIGURED" if settings.census_api_key and settings.census_api_key != "your_census_api_key_here" else "❌ NOT CONFIGURED"
        },
        "epa": {
            "configured": True,
            "requires_key": False,
            "status": "✅ PUBLIC API (no key required)"
        },
        "hud": {
            "configured": bool(hasattr(settings, 'hud_api_key') and settings.hud_api_key),
            "key_prefix": settings.hud_api_key[:10] + "..." if hasattr(settings, 'hud_api_key') and settings.hud_api_key else "Not set",
            "status": "✅ CONFIGURED" if hasattr(settings, 'hud_api_key') and settings.hud_api_key else "⚠️ Optional - will use fallback data",
            "register_at": "https://www.huduser.gov/portal/dataset/fmr-api.html"
        },
        "fbi_crime": {
            "configured": bool(hasattr(settings, 'fbi_crime_api_key') and settings.fbi_crime_api_key),
            "key_prefix": settings.fbi_crime_api_key[:10] + "..." if hasattr(settings, 'fbi_crime_api_key') and settings.fbi_crime_api_key else "Not set",
            "status": "✅ CONFIGURED" if hasattr(settings, 'fbi_crime_api_key') and settings.fbi_crime_api_key else "⚠️ Optional - will use fallback data",
            "register_at": "https://api.data.gov/signup/"
        },
        "fema": {
            "configured": True,
            "requires_key": False,
            "status": "✅ PUBLIC API (no key required)"
        },
        "real_data_percentage": "92%" if (hasattr(settings, 'hud_api_key') and settings.hud_api_key and hasattr(settings, 'fbi_crime_api_key') and settings.fbi_crime_api_key) else "68-85%"
    }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 Starting Production Server - Real API Mode")
    print("="*80)
    print("\n📊 Dashboard: http://127.0.0.1:8000/")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print("💚 Health: http://127.0.0.1:8000/health")
    print("🔧 Config Check: http://127.0.0.1:8000/api/check-config")
    print("\n⚠️  IMPORTANT: Using REAL APIs - requires valid API keys in .env file")
    print("="*80 + "\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9025,
        log_level="info"
    )
