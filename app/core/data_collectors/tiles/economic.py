"""
Tiles-specific Economic Viability Data Collector
Analyzes labor market for installers and warehouse workers, and commercial real estate costs.
"""

import httpx
import asyncio
from typing import Dict, Any, List
from loguru import logger

from app.config import get_settings


class TilesEconomicCollector:
    """
    Collects 10 economic viability data points across 5 categories for Tiles industry:
    
    1. Property Costs (3 points):
       - Real estate cost per sqft (Showroom/Warehouse mix)
       - Property tax rate
       - Interior build-out cost estimate
    
    2. Operating Expenses (3 points):
       - Average commercial rent
       - Utility cost index (High for showrooms)
       - Local wage levels
    
    3. Labor Market (2 points):
       - Tile installer availability
       - Average installer wage
    
    4. Financial Incentives (1 point):
       - Business incentives score
    
    5. Market Trends (1 point):
       - Economic growth indicator
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 5.0) -> Dict[str, Any]:
        """
        Collect comprehensive economic metrics (10 data points)
        """
        try:
            # Step 1: Geocode address
            coordinates = await self._geocode_address(address)
            if not coordinates:
                return self._mock_comprehensive_data()
            
            lat, lng = coordinates
            
            # Step 2: Analyze property costs
            property_metrics = await self._analyze_property_costs(lat, lng, radius_miles)
            
            # Step 3: Analyze operating expenses
            operating_metrics = await self._analyze_operating_expenses(lat, lng, radius_miles)
            
            # Step 4: Analyze labor market
            labor_metrics = await self._analyze_labor_market(lat, lng, radius_miles)
            
            # Step 5: Analyze financial incentives
            incentives_metrics = await self._analyze_incentives(lat, lng)
            
            # Step 6: Analyze market trends
            trends_metrics = await self._analyze_market_trends(lat, lng, radius_miles)
            
            return {
                "success": True,
                "address": address,
                "coordinates": {"lat": lat, "lng": lng},
                **property_metrics,
                **operating_metrics,
                **labor_metrics,
                **incentives_metrics,
                **trends_metrics,
                "data_source": "Google Places API + Estimations - 10 Data Points",
                "industries": ["tiles", "flooring", "interior_design"]
            }
            
        except Exception as e:
            logger.error(f"Tiles economic analysis error: {e}")
            return self._mock_comprehensive_data()
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to coordinates"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": address, "key": self.google_api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            return None
        except Exception:
            return None
    
    async def _analyze_property_costs(self, lat: float, lng: float, radius_miles: float) -> Dict[str, float]:
        """Estimate property costs for Tiles business"""
        # Tiles businesses need showroom (premium) + warehouse (standard)
        # Base commercial: $100/sqft
        base_cost = 100
        
        # Estimate from neighborhood quality
        indicators = ["home_goods_store", "furniture_store", "interior_designer"]
        premium_count = 0
        
        for indicator in indicators:
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "type": indicator,
                "key": self.google_api_key
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()
            if data["status"] == "OK":
                premium_count += len(data.get("results", []))
                
        real_estate_cost = base_cost + (premium_count * 5)
        real_estate_cost = min(350, max(60, real_estate_cost))
        
        return {
            "real_estate_cost_per_sqft": round(real_estate_cost, 2),
            "property_tax_rate_pct": 1.2 if real_estate_cost > 200 else 1.0,
            "construction_cost_per_sqft": round(real_estate_cost * 1.2, 2) # Showroom build-out is expensive
        }

    async def _analyze_operating_expenses(self, lat: float, lng: float, radius_miles: float) -> Dict[str, float]:
        # Tiles showrooms have high lighting/cooling needs
        return {
            "avg_commercial_rent_per_sqft_year": 22.0,
            "utility_cost_index": 115.0, # Higher for showrooms
            "local_wage_level_annual": 45000.0
        }

    async def _analyze_labor_market(self, lat: float, lng: float, radius_miles: float) -> Dict[str, Any]:
        """Analyze labor market for tile installers and warehouse staff"""
        # Search for hardware stores and construction companies
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": int(radius_miles * 1609.34),
            "keyword": "contractor|flooring|construction",
            "key": self.google_api_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
        contractors = len(data.get("results", [])) if data["status"] == "OK" else 0
        availability = 40 + (contractors * 4)
        
        return {
            "installer_availability_score": round(min(100, availability), 1),
            "avg_installer_wage_annual": 52000.0 # Industry average
        }

    async def _analyze_incentives(self, lat: float, lng: float) -> Dict[str, float]:
        return {"business_incentives_score": 55.0}

    async def _analyze_market_trends(self, lat: float, lng: float, radius_miles: float) -> Dict[str, float]:
        return {"economic_growth_indicator": 62.0}

    def _mock_comprehensive_data(self) -> Dict[str, Any]:
        return {
            "success": False,
            "real_estate_cost_per_sqft": 140.0,
            "property_tax_rate_pct": 1.1,
            "construction_cost_per_sqft": 180.0,
            "avg_commercial_rent_per_sqft_year": 21.0,
            "utility_cost_index": 110.0,
            "local_wage_level_annual": 42000.0,
            "installer_availability_score": 65.0,
            "avg_installer_wage_annual": 50000.0,
            "business_incentives_score": 50.0,
            "economic_growth_indicator": 58.0,
            "data_source": "Mock Data"
        }
