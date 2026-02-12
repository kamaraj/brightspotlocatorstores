"""
Tiles-specific Regulatory & Zoning Data Collector
Analyzes commercial/industrial zoning and business licensing for tiles dealers.
"""

import httpx
import asyncio
from typing import Dict, Any, List
from loguru import logger

from app.config import get_settings


class TilesRegulatoryCollector:
    """
    Collects 8 regulatory & zoning data points for Tiles industry:
    
    1. Zoning Requirements (3 points):
       - Zoning compliance score (Commercial/Retail/Light Industrial)
       - Special use permit required
       - Rezoning feasibility
    
    2. Building Code Requirements (2 points):
       - Building code complexity score (Warehouse/Showroom standards)
       - Load-bearing requirement cost (Heavy tiles)
    
    3. Licensing Requirements (2 points):
       - Retail/Wholesale license difficulty
       - Time to obtain business license (days)
    
    4. Processing Timelines (1 point):
       - Average permit processing time (days)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 2.0) -> Dict[str, Any]:
        """
        Collect regulatory & zoning metrics
        """
        try:
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._mock_comprehensive_data()
            
            lat, lng = coordinates
            
            # Simplified for prototype
            zoning_metrics = await self._analyze_zoning(lat, lng, radius_miles)
            licensing_metrics = {"licensing_difficulty": 45.0, "time_to_obtain_license_days": 30}
            building_metrics = {"building_code_complexity": 55.0, "load_bearing_compliance_cost": 12000}
            timeline_metrics = {"avg_permit_processing_days": 45}
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                **zoning_metrics,
                **licensing_metrics,
                **building_metrics,
                **timeline_metrics,
                "data_source": "Google Geocoding API + Estimations",
                "jurisdiction": "Multi-Zonal"
            }
            
        except Exception as e:
            logger.error(f"Tiles regulatory analysis error: {e}")
            return self._mock_comprehensive_data()
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to coordinates"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": address, "key": self.google_api_key}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            return None
        except Exception:
            return None

    async def _analyze_zoning(self, lat: float, lng: float, radius_miles: float) -> Dict[str, Any]:
        """Check for industrial/commercial zones nearby"""
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": int(radius_miles * 1609.34),
            "keyword": "industrial|warehouse|showroom|retail park",
            "key": self.google_api_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
        results = data.get("results", [])
        score = 50 + min(40, len(results) * 5)
        
        return {
            "zoning_compliance_score": float(score),
            "special_use_permit_required": score < 65,
            "rezoning_feasibility_score": 70.0 if score > 60 else 40.0
        }

    def _mock_comprehensive_data(self) -> Dict[str, Any]:
        return {
            "success": False,
            "zoning_compliance_score": 60.0,
            "special_use_permit_required": False,
            "rezoning_feasibility_score": 65.0,
            "licensing_difficulty": 50.0,
            "time_to_obtain_license_days": 35,
            "building_code_complexity": 50.0,
            "load_bearing_compliance_cost": 10000,
            "avg_permit_processing_days": 40,
            "data_source": "Mock Data"
        }
