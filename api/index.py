"""
Vercel Serverless Entry Point for Brightspot Locator AI
Adapted for Vercel's serverless Python environment
"""

import os
import sys

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import time
import json

# Import collectors
from app.core.data_collectors.demographics import DemographicsCollector
from app.core.data_collectors.competition_enhanced import CompetitionCollectorEnhanced
from app.core.data_collectors.accessibility_enhanced import AccessibilityCollectorEnhanced
from app.core.data_collectors.safety_enhanced import SafetyCollectorEnhanced
from app.core.data_collectors.economic_enhanced import EconomicCollectorEnhanced
from app.core.data_collectors.regulatory import RegulatoryCollector
from app.utils.timing_xai import PerformanceTracker, DataPointExplainer
import googlemaps

# OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = FastAPI(title="Brightspot Locator AI - Vercel Edition")

# CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration from environment
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", os.environ.get("PLACES_API_KEY", ""))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")

# Templates - use path relative to this file
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "templates")
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static")

templates = None
try:
    templates = Jinja2Templates(directory=template_dir)
except Exception as e:
    print(f"Templates not available: {e}")

# OpenAI client for AI explanations
openai_client = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"OpenAI client initialization failed: {e}")


async def generate_ai_explanation(category: str, data: Dict[str, Any], score: float) -> Dict[str, str]:
    """Generate AI-powered explanation using OpenAI"""
    if not openai_client:
        return {
            "interpretation": f"Score of {score:.1f} indicates {'strong' if score >= 70 else 'moderate' if score >= 50 else 'limited'} potential.",
            "recommendation": "Review detailed metrics for specific insights."
        }
    
    try:
        # Create prompt for OpenAI
        prompt = f"""Analyze this {category} data for a childcare location and provide a brief interpretation and recommendation.

Category: {category}
Score: {score}/100
Key Metrics: {json.dumps({k: v for k, v in data.items() if isinstance(v, (int, float, str)) and not k.endswith('_explanation')}, indent=2)[:1000]}

Provide a JSON response with:
1. "interpretation": 2-3 sentences explaining what the score means for childcare business
2. "recommendation": 1-2 specific actionable recommendations

Return ONLY valid JSON."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"OpenAI explanation error: {e}")
        return {
            "interpretation": f"Score of {score:.1f} suggests {'favorable' if score >= 60 else 'moderate'} conditions for {category}.",
            "recommendation": "Analyze individual metrics for detailed insights."
        }


async def validate_and_correct_address(address: str) -> Dict[str, Any]:
    """Validate and correct address using Google Geocoding API"""
    if not GOOGLE_MAPS_API_KEY:
        return {
            "success": False,
            "error": "Google Maps API key not configured",
            "original_address": address
        }
    
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        geocode_result = gmaps.geocode(address)
        
        if not geocode_result:
            return {
                "success": False,
                "error": f"Address not found: '{address}'",
                "original_address": address
            }
        
        result = geocode_result[0]
        formatted_address = result.get("formatted_address", address)
        location = result.get("geometry", {}).get("location", {})
        
        return {
            "success": True,
            "original_address": address,
            "corrected_address": formatted_address,
            "corrected": formatted_address != address,
            "location": location,
            "components": result.get("address_components", [])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_address": address
        }


def _calculate_scores(results: Dict[str, Any]) -> Dict[str, float]:
    """Calculate category scores"""
    scores = {}
    
    # Demographics
    demo = results.get("demographics", {})
    if demo:
        children = demo.get("children_0_5_count", 0)
        income = demo.get("median_household_income", 50000)
        demo_score = min(100, (children / 20) + (income / 2000))
        scores["demographics"] = round(min(100, max(0, demo_score)), 1)
    
    # Competition
    comp = results.get("competition", {})
    if comp:
        centers = comp.get("existing_centers_count", 0)
        gap = comp.get("market_gap_score", 50)
        comp_score = (100 - min(100, centers * 5)) * 0.5 + gap * 0.5
        scores["competition"] = round(min(100, max(0, comp_score)), 1)
    
    # Accessibility
    access = results.get("accessibility", {})
    if access:
        scores["accessibility"] = round(access.get("accessibility_score", 60), 1)
    
    # Safety
    safe = results.get("safety", {})
    if safe:
        crime = safe.get("crime_rate_index", 50)
        scores["safety"] = round(100 - min(100, crime), 1)
    
    # Economic
    econ = results.get("economic", {})
    if econ:
        scores["economic"] = round(econ.get("economic_viability_score", 55), 1)
    
    # Regulatory
    reg = results.get("regulatory", {})
    if reg:
        scores["regulatory"] = round(reg.get("zoning_compliance_score", 60), 1)
    
    # Overall
    weights = {"demographics": 0.25, "competition": 0.20, "accessibility": 0.15,
               "safety": 0.20, "economic": 0.10, "regulatory": 0.10}
    weighted_sum = sum(scores.get(cat, 50) * weight for cat, weight in weights.items())
    scores["overall"] = round(weighted_sum, 1)
    
    return scores


async def collect_data_parallel(address: str, radius_miles: float, tracker: PerformanceTracker) -> Dict[str, Any]:
    """Collect all data in parallel"""
    
    # Validate address
    with tracker.track("address_validation"):
        address_info = await validate_and_correct_address(address)
        if not address_info.get("success"):
            return {"error": address_info.get("error"), "original_address": address}
    
    corrected_address = address_info.get("corrected_address", address)
    location = address_info.get("location", {})
    latitude = location.get("lat")
    longitude = location.get("lng")
    
    # Initialize collectors
    demographics_collector = DemographicsCollector()
    competition_collector = CompetitionCollectorEnhanced()
    accessibility_collector = AccessibilityCollectorEnhanced()
    safety_collector = SafetyCollectorEnhanced()
    economic_collector = EconomicCollectorEnhanced()
    regulatory_collector = RegulatoryCollector()
    
    collection_start = time.time()
    
    with tracker.track("parallel_collection"):
        results = await asyncio.gather(
            demographics_collector.collect(corrected_address),
            competition_collector.collect(corrected_address, radius_miles),
            accessibility_collector.collect(corrected_address, radius_miles),
            safety_collector.collect(corrected_address, radius_miles),
            economic_collector.collect(corrected_address, radius_miles),
            regulatory_collector.collect(corrected_address),
            return_exceptions=True
        )
    
    collection_time_ms = round((time.time() - collection_start) * 1000, 2)
    
    # Unpack results
    (demographics_data, competition_data, accessibility_data, 
     safety_data, economic_data, regulatory_data) = results
    
    # Handle exceptions
    def safe_data(data, default=None):
        if isinstance(data, Exception):
            return default or {"error": str(data), "metrics": {}, "score": 0}
        return data or {"error": "No data", "metrics": {}, "score": 0}
    
    demographics_data = safe_data(demographics_data)
    competition_data = safe_data(competition_data)
    accessibility_data = safe_data(accessibility_data)
    safety_data = safe_data(safety_data)
    economic_data = safe_data(economic_data)
    regulatory_data = safe_data(regulatory_data)
    
    # Add collection time
    for data in [demographics_data, competition_data, accessibility_data, 
                 safety_data, economic_data, regulatory_data]:
        if isinstance(data, dict) and "collection_time_ms" not in data:
            data["collection_time_ms"] = collection_time_ms / 6
    
    categories = {
        "demographics": demographics_data,
        "competition": competition_data,
        "accessibility": accessibility_data,
        "safety": safety_data,
        "economic": economic_data,
        "regulatory": regulatory_data
    }
    
    # Calculate scores
    scores = _calculate_scores(categories)
    
    # Add scores and explanations to categories
    metadata_fields = {
        "success", "address", "coordinates", "data_source", "note", "score", 
        "radius_miles", "collection_time_ms", "metrics_count", "explanation",
        "error", "metrics", "search_radius_miles", "centers_analyzed",
        "total_population", "land_area_sqmi", "jurisdiction", "state", "centers_details"
    }
    
    for cat_name, score in scores.items():
        if cat_name in categories and cat_name != "overall":
            categories[cat_name]["score"] = score
            
            # Count metrics
            metrics_count = 0
            for k in categories[cat_name].keys():
                if k not in metadata_fields and not k.endswith("_explanation"):
                    val = categories[cat_name][k]
                    if isinstance(val, (int, float, str, bool)):
                        metrics_count += 1
            categories[cat_name]["metrics_count"] = metrics_count
            
            # Generate AI explanation
            try:
                explanation = await generate_ai_explanation(cat_name, categories[cat_name], score)
                categories[cat_name]["explanation"] = explanation
            except Exception as e:
                categories[cat_name]["explanation"] = {
                    "interpretation": f"Analysis complete with score {score:.1f}",
                    "recommendation": "Review metrics for details"
                }
    
    # Count total data points
    data_points_collected = sum(
        cat_data.get("metrics_count", 0) for cat_data in categories.values() if isinstance(cat_data, dict)
    )
    
    return {
        "address": corrected_address,
        "original_address": address,
        "overall_score": scores.get("overall", 0),
        "categories": categories,
        "data_points_collected": data_points_collected,
        "address_validation": address_info,
        "analysis_timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def home(request: Request):
    """Home page"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("""
    <html>
    <head><title>Brightspot Locator AI</title></head>
    <body>
        <h1>🏢 Brightspot Locator AI</h1>
        <p>API is running. Use <a href="/docs">/docs</a> for API documentation.</p>
        <p>Or POST to <code>/api/v1/analyze</code> with {"address": "your address", "radius_miles": 2.0}</p>
    </body>
    </html>
    """)


@app.get("/static/{path:path}")
async def serve_static(path: str):
    """Serve static files"""
    file_path = os.path.join(static_dir, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


@app.post("/api/v1/analyze")
async def analyze_location(request: Request):
    """Analyze location for childcare potential"""
    try:
        body = await request.json()
        address = body.get("address", "")
        radius_miles = body.get("radius_miles", 3.0)
        
        if not address:
            raise HTTPException(status_code=400, detail="Address is required")
        
        start_time = time.time()
        tracker = PerformanceTracker()
        
        result = await collect_data_parallel(address, radius_miles, tracker)
        
        total_time = time.time() - start_time
        result["performance"] = {
            "total_time_seconds": round(total_time, 2),
            "collection_breakdown": tracker.get_report(),
            "openai_enabled": openai_client is not None
        }
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "vercel-1.0",
        "environment": "vercel",
        "features": {
            "google_maps": bool(GOOGLE_MAPS_API_KEY),
            "openai": bool(OPENAI_API_KEY) and openai_client is not None,
            "census": bool(CENSUS_API_KEY)
        }
    }


@app.get("/api/check-config")
async def check_config():
    """Check API configuration"""
    return {
        "google_maps_configured": bool(GOOGLE_MAPS_API_KEY),
        "openai_configured": bool(OPENAI_API_KEY),
        "census_configured": bool(CENSUS_API_KEY),
        "openai_client_ready": openai_client is not None
    }


# Export for Vercel
handler = app
