"""
Fast Demo Server - Childcare Location Intelligence
Uses mock data for instant responses
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from typing import Dict, Any
import asyncio

app = FastAPI(title="Brightspot Locator AI - Fast Demo")

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

try:
    templates = Jinja2Templates(directory="app/templates")
except:
    templates = None

# Favicon route
@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/favicon.ico")


def get_mock_data(address: str) -> Dict[str, Any]:
    """Return instant mock data"""
    return {
        "address": address,
        "overall_score": 72.5,
        "recommendation": "GOOD ⭐⭐⭐⭐ - Suitable location with good potential",
        "data_points_collected": 66,
        "analysis_time_ms": 350.0,
        "categories": {
            "demographics": {
                "score": 78.0,
                "data": {
                    "children_0_5_count": 1500,
                    "population_density": 4200.5,
                    "birth_rate": 12.5,
                    "median_household_income": 85000,
                    "dual_income_rate": 68.5,
                    "working_mothers_rate": 72.3,
                    "population_growth_rate": 2.1,
                    "family_household_rate": 65.2
                }
            },
            "competition": {
                "score": 65.0,
                "data": {
                    "existing_centers_count": 8,
                    "total_licensed_capacity": 450,
                    "market_saturation_index": 2.35,
                    "avg_competitor_rating": 4.2,
                    "premium_facilities_count": 3,
                    "market_gap_score": 65.0,
                    "demand_supply_ratio": 1.8,
                    "nearest_competitor_miles": 0.75,
                    "competitive_intensity_score": 68.5
                }
            },
            "accessibility": {
                "score": 74.0,
                "data": {
                    "avg_commute_minutes": 25.5,
                    "transit_score": 72.0,
                    "walk_score_to_transit": 65.0,
                    "morning_rush_score": 58.0,
                    "parking_availability_score": 82.0,
                    "highway_visibility_score": 78.0
                }
            },
            "safety": {
                "score": 82.0,
                "data": {
                    "crime_rate_index": 35.2,
                    "pedestrian_safety_score": 75.0,
                    "air_quality_index": 45.0,
                    "traffic_accident_rate": 4.2,
                    "neighborhood_safety_perception": 78.0
                }
            },
            "economic": {
                "score": 68.0,
                "data": {
                    "real_estate_cost_per_sqft": 165.50,
                    "property_tax_rate_pct": 1.25,
                    "childcare_worker_availability_score": 68.0,
                    "avg_childcare_worker_wage": 42000,
                    "business_incentives_score": 55.0,
                    "economic_growth_indicator": 62.0
                }
            },
            "regulatory": {
                "score": 71.0,
                "data": {
                    "zoning_compliance_score": 75.0,
                    "rezoning_feasibility_score": 65.0,
                    "licensing_difficulty_score": 48.0,
                    "time_to_obtain_license_days": 90,
                    "avg_permit_processing_days": 45
                }
            }
        },
        "timing": {
            "demographics_ms": 45.2,
            "competition_ms": 82.5,
            "accessibility_ms": 68.3,
            "safety_ms": 51.7,
            "economic_ms": 43.9,
            "regulatory_ms": 38.4,
            "xai_generation_ms": 20.0
        },
        "key_insights": [
            "Strong demographic profile with 1,500 children aged 0-5",
            "Good market opportunity with 65% gap score",
            "Excellent safety metrics (82/100)",
            "Competitive but not oversaturated market",
            "Above-average income levels support premium pricing"
        ]
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve dashboard"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("<h1>Dashboard template not found</h1>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0-fast"}


@app.post("/api/v1/analyze")
async def analyze_location(request: Request):
    """Analyze location - instant response with mock data"""
    # Get JSON body
    body = await request.json()
    address = body.get("address", "Unknown Address")
    radius = body.get("radius_miles", 2.0)
    
    # Simulate minimal processing time
    await asyncio.sleep(0.35)
    
    results = get_mock_data(address)
    results["timestamp"] = "2025-12-05T19:10:00"
    return JSONResponse(results)


@app.get("/api/demo-data")
async def get_demo_data():
    """Get demo data for testing"""
    return get_mock_data("1600 Amphitheatre Parkway, Mountain View, CA 94043")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Starting Fast Demo Server")
    print("="*80)
    print("\n📊 Dashboard: http://127.0.0.1:8000/")
    print("📖 API Docs: http://127.0.0.1:8000/docs")
    print("💚 Health: http://127.0.0.1:8000/health\n")
    print("⚡ Using mock data for instant responses (no API delays)")
    print("="*80 + "\n")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9025,
        log_level="info"
    )
