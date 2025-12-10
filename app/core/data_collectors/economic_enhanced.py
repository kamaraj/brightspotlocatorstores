"""
Enhanced Economic Viability Data Collector
Comprehensive analysis with 10 data points across 5 categories
"""

import httpx
import asyncio
from typing import Dict, Any, List
from loguru import logger

from app.config import get_settings


class EconomicCollectorEnhanced:
    """
    Collects 10 economic viability data points across 5 categories:
    
    1. Property Costs (3 points):
       - Real estate cost per sqft
       - Property tax rate
       - Construction cost estimates
    
    2. Operating Expenses (3 points):
       - Average commercial rent
       - Utility cost index
       - Local wage levels
    
    3. Labor Market (2 points):
       - Childcare worker availability
       - Average worker wage
    
    4. Financial Incentives (1 point):
       - Business incentives score
    
    5. Market Trends (1 point):
       - Economic growth indicator
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.google_api_key = self.settings.places_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        
    async def collect(self, address: str, radius_miles: float = 2.0) -> Dict[str, Any]:
        """
        Collect comprehensive economic metrics (10 data points)
        
        Args:
            address: Full street address
            radius_miles: Search radius (default 2 miles)
            
        Returns:
            Dictionary with 10 economic metrics across 5 categories
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
                "data_source": "Google Places API + Estimations - 10 Data Points"
            }
            
        except Exception as e:
            logger.error(f"Enhanced economic analysis error: {e}")
            return self._mock_comprehensive_data()
    
    async def _geocode_address(self, address: str) -> tuple[float, float] | None:
        """Convert address to coordinates"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": address, "key": self.google_api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            
            return None
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def _analyze_property_costs(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float
    ) -> Dict[str, float]:
        """
        Analyze property-related costs
        Returns: real_estate_cost_per_sqft, property_tax_rate, construction_cost_estimate
        
        Note: Production should use Zillow API, CoStar, or local MLS data
        """
        try:
            # Estimate real estate cost from neighborhood quality indicators
            premium_indicators = [
                "shopping_mall", "university", "hospital", "movie_theater"
            ]
            
            premium_count = 0
            premium_ratings = []
            
            for indicator in premium_indicators:
                url = f"{self.base_url}/place/nearbysearch/json"
                params = {
                    "location": f"{lat},{lng}",
                    "radius": int(radius_miles * 1609.34),
                    "type": indicator,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    data = response.json()
                
                if data["status"] == "OK":
                    results = data.get("results", [])
                    # Count highly-rated premium amenities
                    for place in results:
                        rating = place.get("rating", 0)
                        if rating >= 4.0:
                            premium_count += 1
                            premium_ratings.append(rating)
                
                await asyncio.sleep(0.1)
            
            # Base commercial real estate: $120/sqft
            # Premium amenities add $20/sqft each
            base_cost = 120
            real_estate_cost = base_cost + (premium_count * 20)
            real_estate_cost = min(400, max(50, real_estate_cost))  # Cap $50-400/sqft
            
            # Property tax rate estimation (US average: 1.1%, range 0.3-2.5%)
            # Higher real estate costs often correlate with higher taxes
            property_tax_rate = 1.1
            if real_estate_cost > 250:
                property_tax_rate = 1.8
            elif real_estate_cost > 180:
                property_tax_rate = 1.4
            elif real_estate_cost < 100:
                property_tax_rate = 0.8
            
            # Construction cost estimate (typically 1.3-1.5x real estate cost for commercial)
            construction_multiplier = 1.4
            construction_cost = real_estate_cost * construction_multiplier
            
            return {
                "real_estate_cost_per_sqft": round(real_estate_cost, 2),
                "property_tax_rate_pct": round(property_tax_rate, 2),
                "construction_cost_per_sqft": round(construction_cost, 2)
            }
            
        except Exception as e:
            logger.debug(f"Property cost analysis error: {e}")
            return {
                "real_estate_cost_per_sqft": 150.0,
                "property_tax_rate_pct": 1.2,
                "construction_cost_per_sqft": 210.0
            }
    
    async def _analyze_operating_expenses(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float
    ) -> Dict[str, float]:
        """
        Analyze ongoing operating expenses
        Returns: avg_commercial_rent, utility_cost_index, local_wage_level
        """
        try:
            # Estimate commercial rent from real estate activity
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "keyword": "office space|commercial rental|real estate",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            real_estate_activity = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Base rent: $18/sqft/year, adjusted for activity
            # High activity = expensive area
            base_rent = 18.0
            commercial_rent = base_rent + (real_estate_activity * 1.5)
            commercial_rent = min(45, max(10, commercial_rent))  # Cap $10-45/sqft/year
            
            # Utility cost index (100 = national average)
            # Estimate from climate indicators (extreme temps = higher utilities)
            # For simplicity, base on latitude (further from equator = more heating/cooling)
            latitude_factor = abs(lat - 35) / 15  # 35°N is moderate climate
            utility_index = 100 + (latitude_factor * 20)
            utility_index = min(150, max(80, utility_index))
            
            # Local wage level (estimate from business density and ratings)
            business_types = ["restaurant", "retail_store", "cafe"]
            all_businesses = []
            
            for biz_type in business_types:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": int(radius_miles * 1609.34),
                    "type": biz_type,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    data = response.json()
                
                if data["status"] == "OK":
                    all_businesses.extend(data.get("results", []))
                
                await asyncio.sleep(0.1)
            
            # Price level indicates local wage level (1-4 scale, where 4 = expensive)
            price_levels = [b.get("price_level", 2) for b in all_businesses if "price_level" in b]
            avg_price_level = sum(price_levels) / len(price_levels) if price_levels else 2
            
            # Map price level to annual wage
            # Level 1 = $28K, Level 4 = $40K for childcare workers
            wage_base = 28000
            wage_adjustment = (avg_price_level - 1) * 4000
            local_wage = wage_base + wage_adjustment
            
            return {
                "avg_commercial_rent_per_sqft_year": round(commercial_rent, 2),
                "utility_cost_index": round(utility_index, 1),
                "local_wage_level_annual": round(local_wage, 0)
            }
            
        except Exception as e:
            logger.debug(f"Operating expense analysis error: {e}")
            return {
                "avg_commercial_rent_per_sqft_year": 20.0,
                "utility_cost_index": 100.0,
                "local_wage_level_annual": 32000.0
            }
    
    async def _analyze_labor_market(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float
    ) -> Dict[str, Any]:
        """
        Analyze labor market for childcare workers
        Returns: childcare_worker_availability, avg_childcare_worker_wage
        
        Note: Production should use BLS data and local job boards
        """
        try:
            # Search for educational institutions (teachers often transition to childcare)
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "type": "school",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            schools = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Search for existing childcare centers (competitor workers could transfer)
            params["keyword"] = "childcare|daycare|preschool"
            params.pop("type")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            existing_centers = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Worker availability score (0-100, higher = more available workers)
            # More schools = more potential teachers
            # More existing centers = competitive labor market (lower availability)
            availability = 50 + (schools * 5) - (existing_centers * 3)
            availability = max(20, min(100, availability))
            
            # Average childcare worker wage
            # US median: $28,520 (BLS 2023)
            # Adjust for local cost of living (estimated from schools and price levels)
            base_wage = 28520
            
            # Areas with many schools tend to pay better
            wage_adjustment = schools * 500
            avg_wage = base_wage + wage_adjustment
            avg_wage = min(45000, max(24000, avg_wage))
            
            return {
                "childcare_worker_availability_score": round(availability, 1),
                "avg_childcare_worker_wage": round(avg_wage, 0)
            }
            
        except Exception as e:
            logger.debug(f"Labor market analysis error: {e}")
            return {
                "childcare_worker_availability_score": 60.0,
                "avg_childcare_worker_wage": 30000.0
            }
    
    async def _analyze_incentives(self, lat: float, lng: float) -> Dict[str, float]:
        """
        Analyze business incentives and support
        Returns: business_incentives_score
        
        Note: Production should query local economic development databases
        """
        try:
            # Look for indicators of business-friendly environment
            # Government offices, economic development centers, business associations
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 8046,  # 5 miles
                "keyword": "economic development|chamber of commerce|business center|small business",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            support_orgs = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Check for signs of development activity
            params["keyword"] = "new construction|development|commercial building"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            development_activity = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Business incentives score (0-100)
            # More support organizations and development = better incentives
            incentives_score = 40  # Base score
            incentives_score += min(30, support_orgs * 10)  # Up to 30 points
            incentives_score += min(30, development_activity * 5)  # Up to 30 points
            
            return {
                "business_incentives_score": round(incentives_score, 1)
            }
            
        except Exception as e:
            logger.debug(f"Incentives analysis error: {e}")
            return {
                "business_incentives_score": 50.0
            }
    
    async def _analyze_market_trends(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float
    ) -> Dict[str, float]:
        """
        Analyze economic growth indicators
        Returns: economic_growth_indicator
        """
        try:
            # Look for growth indicators: new businesses, construction, development
            growth_keywords = [
                "new", "opening soon", "coming soon", "under construction"
            ]
            
            new_business_count = 0
            
            for keyword in growth_keywords:
                url = f"{self.base_url}/place/nearbysearch/json"
                params = {
                    "location": f"{lat},{lng}",
                    "radius": int(radius_miles * 1609.34),
                    "keyword": keyword,
                    "key": self.google_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=10.0)
                    data = response.json()
                
                if data["status"] == "OK":
                    new_business_count += len(data.get("results", []))
                
                await asyncio.sleep(0.1)
            
            # Check for established businesses (baseline economic health)
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": int(radius_miles * 1609.34),
                "type": "establishment",
                "key": self.google_api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
            
            total_businesses = len(data.get("results", [])) if data["status"] == "OK" else 0
            
            # Growth indicator (0-100, higher = stronger growth)
            # New business ratio: (new / total) * 100
            if total_businesses > 0:
                growth_ratio = (new_business_count / total_businesses) * 100
                # Scale to 0-100 (10% new businesses = strong growth)
                growth_indicator = min(100, growth_ratio * 10)
            else:
                growth_indicator = 50.0  # Default moderate
            
            # Bonus points for absolute number of new businesses
            if new_business_count > 10:
                growth_indicator = min(100, growth_indicator + 20)
            elif new_business_count > 5:
                growth_indicator = min(100, growth_indicator + 10)
            
            return {
                "economic_growth_indicator": round(growth_indicator, 1)
            }
            
        except Exception as e:
            logger.debug(f"Market trends analysis error: {e}")
            return {
                "economic_growth_indicator": 55.0
            }
    
    def _mock_comprehensive_data(self) -> Dict[str, Any]:
        """Return mock data when API fails"""
        return {
            "success": False,
            "real_estate_cost_per_sqft": 150.0,
            "property_tax_rate_pct": 1.2,
            "construction_cost_per_sqft": 210.0,
            "avg_commercial_rent_per_sqft_year": 20.0,
            "utility_cost_index": 100.0,
            "local_wage_level_annual": 32000.0,
            "childcare_worker_availability_score": 60.0,
            "avg_childcare_worker_wage": 30000.0,
            "business_incentives_score": 50.0,
            "economic_growth_indicator": 55.0,
            "data_source": "Mock Data"
        }
